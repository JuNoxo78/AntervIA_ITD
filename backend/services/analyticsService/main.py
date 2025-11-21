import threading
import time
import cv2
import numpy as np
import requests
import os
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from starlette.middleware.cors import CORSMiddleware
from ultralytics import YOLO

# --- Configuración ---

# Configuración del modelo YOLO
try:
    YOLO_MODEL = YOLO('resources/yolov8n.pt')
    print("Modelo YOLO cargado exitosamente.")
except Exception as e:
    print(f"Error al cargar el modelo YOLO: {e}")
    YOLO_MODEL = None

# Constantes para detección de personas
CLASS_ID_PERSON = 0  # La clase 0 en COCO es "person"
COLOR_AZUL = (255, 0, 0)  # Color BGR para cuadros de detección
GROSOR_LINEA = 2

# URL del backend de Spring Boot (a donde enviaremos las alertas)
# Asegúrate de que esta URL sea accesible desde este servicio de Python
SPRING_BOOT_ALERT_URL = "http://localhost:8080/api/internal/alerts"

# --- Aplicación FastAPI ---
app = FastAPI(
    title="Servicio de Analítica de Video",
    description="Procesa streams RTSP y envía alertas a Spring Boot."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],  # Ajustar según puerto de desarrollo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Modelos de Datos (Pydantic) ---
# Esto es lo que recibimos de Spring Boot
class CameraRequest(BaseModel):
    camera_id: int
    rtsp_url: str

# Esto es lo que enviamos A Spring Boot
class AlertPayload(BaseModel):
    camera_id: int
    timestamp: str
    event_type: str  # Ej: "HIGH_RISK_AGGRESSION", "LOITERING"
    details: str
    clip_path: str  # Ej: "/clips/cam_123_20251109173000.mp4"

# --- Estado en Memoria ---
# Usamos un diccionario para rastrear los hilos de análisis activos.
# { 123: threading.Event(), 124: threading.Event() }
# Usamos un 'Event' para poder enviar una señal de "parada" al hilo.
active_analysis_threads = {}

# --- Lógica de Análisis (se ejecuta en un Hilo) ---

def detect_persons_in_frame(frame: np.ndarray, camera_id: int):
    """
    Detecta personas en un frame usando YOLO.
    Dibuja cuadros azules alrededor de las personas detectadas.
    Retorna el frame con las detecciones dibujadas y el número de personas detectadas.
    """
    if YOLO_MODEL is None:
        return frame, 0

    # Detecta solo personas con confianza >= 0.6
    results = YOLO_MODEL(frame, classes=[CLASS_ID_PERSON], conf=0.6, verbose=False)

    num_persons = 0

    # Dibujar cuadros azules alrededor de cada persona detectada
    for box in results[0].boxes:
        num_persons += 1

        # Obtiene las coordenadas del cuadro
        x1, y1, x2, y2 = box.xyxy[0]
        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

        # Dibuja el rectángulo azul
        cv2.rectangle(
            img=frame,
            pt1=(x1, y1),
            pt2=(x2, y2),
            color=COLOR_AZUL,
            thickness=GROSOR_LINEA
        )

        # Añade etiqueta de confianza
        conf = float(box.conf[0])
        label = f"Persona: {conf:.2f}"
        cv2.putText(frame, label, (x1, y1 - 10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLOR_AZUL, 2)

    # Imprime en consola si se detectaron personas

    if num_persons > 0:
        print(f"[Cámara {camera_id}]: {num_persons} persona(s) detectada(s)")

    return frame, num_persons

def capture_frame_five_s(camera_id: int, frame: np.ndarray, current_time: float, last_saved_time: float, clips_dir: str):
    """
    Guarda un frame cada 5 segundos en la carpeta clips.
    Retorna el tiempo actualizado de la última captura.
    """
    if current_time - last_saved_time >= 5:
        filename = f"cam_{camera_id}_{int(current_time)}.jpg"
        filepath = os.path.join(clips_dir, filename)
        cv2.imwrite(filepath, frame)
        print(f"[Cámara {camera_id}]: Frame guardado en {filepath}")
        return current_time
    return last_saved_time

def rescale_frame(frame, scale=0.75):
    width = int(frame.shape[1] * scale)
    height = int(frame.shape[0] * scale)
    dimensions = (width, height)

    return cv2.resize(frame, dimensions, interpolation=cv2.INTER_AREA)

def analyze_camera_stream(camera_id: int, rtsp_url: str, stop_event: threading.Event):
    """
    Esta función se ejecuta en un hilo separado por cada cámara.
    Maneja la conexión, el procesamiento y la reconexión.
    """
    print(f"[Cámara {camera_id}]: Iniciando hilo de análisis para {rtsp_url}")

    clips_dir = os.path.join(os.path.dirname(__file__), "clips")
    os.makedirs(clips_dir, exist_ok=True)

    # Bucle "Supervisor": mientras no nos digan que paremos, intentamos conectarnos.
    last_saved_time = time.time()
    frame_count = 0  # Contador para procesar YOLO cada N frames
    last_detection_frame = None  # Guardar último frame con detecciones

    while not stop_event.is_set():
        cap = cv2.VideoCapture(rtsp_url)

        # Optimización: Reducir buffer para disminuir latencia
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        if not cap.isOpened():
            print(f"[Cámara {camera_id}]: Error al conectar. Reintentando en 15 segundos...")
            # Espera 15s antes de reintentar para no saturar
            stop_event.wait(15)
            continue

        print(f"[Cámara {camera_id}]: Conexión exitosa. Empezando análisis...")

        # Bucle "Procesamiento": mientras la cámara esté conectada
        while cap.isOpened() and not stop_event.is_set():
            ret, frame = cap.read()

            # Si 'ret' es False, perdimos la conexión (cámara apagada, red, etc.)
            if not ret:
                print(f"[Cámara {camera_id}]: Stream perdido.")
                break  # Sale del bucle de procesamiento y vuelve al supervisor

            # Redimensiona el frame
            frame = rescale_frame(frame, 0.6)

            # Optimización: Procesar YOLO solo cada 3 frames para mejor rendimiento
            if frame_count % 10 == 0:
                frame_with_detections, num_persons = detect_persons_in_frame(frame, camera_id)
                last_detection_frame = frame_with_detections.copy()
            else:
                # Usar el último frame procesado si existe, sino el frame actual
                frame_with_detections = last_detection_frame if last_detection_frame is not None else frame

            frame_count += 1

            # # Guarda el frame cada 5 segundos
            # current_time = time.time()
            # last_saved_time = capture_frame_five_s(camera_id, frame_with_detections, current_time, last_saved_time, clips_dir)

            cv2.imshow(f"AntervIA - Camera Detection {camera_id}", frame_with_detections)
            cv2.waitKey(1)

        # --- Fin del bucle de procesamiento ---
        cap.release()
        cv2.destroyAllWindows()  # Destruímos todas las ventanas
        if not stop_event.is_set():
            print(f"[Cámara {camera_id}]: Conexión perdida. Preparando para reconectar.")

    print(f"[Cámara {camera_id}]: Hilo de análisis detenido limpiamente.")

# --- Endpoints de la API ---
@app.post("/analyze")
async def start_analysis(request: CameraRequest):
    """
    Endpoint para iniciar el análisis de una cámara.
    Spring Boot llama a este endpoint.
    """
    camera_id = request.camera_id
    rtsp_url = request.rtsp_url

    if camera_id in active_analysis_threads:
        print(f"Advertencia: Se intentó iniciar análisis para {camera_id}, pero ya estaba activo.")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El análisis para esta cámara ya está en ejecución."
        )

    # Creamos un "evento" para poder detener el hilo más tarde
    stop_event = threading.Event()

    # Creamos el hilo (thread)
    analysis_thread = threading.Thread(
        target=analyze_camera_stream,
        args=(camera_id, rtsp_url, stop_event),
        daemon=True  # Hilo 'daemon' para que termine si la app principal muere
    )

    # Guardamos la referencia al evento de parada
    active_analysis_threads[camera_id] = stop_event

    # Iniciamos el hilo
    analysis_thread.start()

    print(f"Análisis iniciado para cámara {camera_id}.")
    return {"status": "success", "message": f"Análisis iniciado para la cámara {camera_id}."}

@app.post("/stop-analyze")
async def stop_analysis(request: CameraRequest):
    """
    Endpoint para detener el análisis de una cámara.
    Spring Boot llama a esto cuando se elimina una cámara.
    """
    camera_id = request.camera_id

    if camera_id not in active_analysis_threads:
        print(f"Advertencia: Se intentó detener análisis para {camera_id}, pero no estaba activo.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontró ningún análisis activo para esta cámara."
        )

    # Obtenemos el evento de parada y le damos la señal
    stop_event = active_analysis_threads[camera_id]
    stop_event.set()  # Esto hará que el bucle 'while not stop_event.is_set()' termine

    # Limpiamos el diccionario
    del active_analysis_threads[camera_id]

    print(f"Análisis detenido para cámara {camera_id}.")
    return {"status": "success", "message": f"Análisis detenido para la cámara {camera_id}."}