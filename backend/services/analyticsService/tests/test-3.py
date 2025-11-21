import cv2
from ultralytics import YOLO

# --- 1. Configuración ---

# Carga el modelo YOLOv8 Nano
try:
    model = YOLO('../resources/yolov8n.pt')
except Exception as e:
    print(f"Error al cargar el modelo YOLO: {e}")
    exit()

# La clase 0 en el dataset COCO es "person"
CLASS_ID_PERSON = 0

# Define el color AZUL en formato BGR (el que usa OpenCV)
# B=255, G=0, R=0
COLOR_AZUL = (255, 0, 0)

# Grosor del cuadro
GROSOR_LINEA = 2

# --- 2. Fuente de Video ---

# Usamos '0' para la cámara web local.
# Cámbialo por una ruta de archivo si quieres (ej. "video.mp4")
video_source = 0
cap = cv2.VideoCapture(video_source)

if not cap.isOpened():
    print(f"Error: No se pudo abrir la fuente de video: {video_source}")
    exit()

print("Fuente de video abierta. Presiona 'q' para salir.")

# --- 3. Bucle Principal de Detección ---

while True:
    # Lee un frame del video
    ret, frame = cap.read()
    if not ret:
        print("Fin del video o error de lectura.")
        break

    # --- 4. Detección con YOLO ---
    # Busca SÓLO personas (class=0)
    results = model(frame, classes=[CLASS_ID_PERSON], conf=0.6, verbose=False)

    # --- 5. Dibujar Cuadros Azules ---
    # Itera sobre cada detección en el frame actual
    for box in results[0].boxes:
        # Obtiene las coordenadas del cuadro (xyxy format)
        x1, y1, x2, y2 = box.xyxy[0]

        # Convierte las coordenadas a enteros para OpenCV
        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

        # Dibuja el rectángulo azul
        cv2.rectangle(
            img=frame,  # El frame donde dibujar
            pt1=(x1, y1),  # Esquina superior izquierda
            pt2=(x2, y2),  # Esquina inferior derecha
            color=COLOR_AZUL,  # Color (BGR)
            thickness=GROSOR_LINEA
        )

        # (Opcional) Añadir etiqueta de confianza
        conf = float(box.conf[0])
        label = f"Persona: {conf:.2f}"
        cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLOR_AZUL, 2)

    # --- 6. Mostrar Resultado ---
    # Muestra el frame con las detecciones
    cv2.imshow("AntervIA - Detección Local", frame)

    # Lógica para salir (presiona 'q')
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# --- 7. Limpieza ---
print("Cerrando...")
cap.release()
cv2.destroyAllWindows()