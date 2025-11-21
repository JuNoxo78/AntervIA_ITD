import cv2
import numpy as np

# --- Configuración ---
# Rutas a los archivos del modelo DNN
prototxt_path = '../resources/deploy.prototxt.txt'
caffe_model_path = '../resources/res10_300x300_ssd_iter_140000.caffemodel'

# Ruta a tu video
ruta_video = 0

# Umbral de confianza: solo mostrará detecciones > 50%
confianza_minima = 0.5

# Configuración del cuadro
color_cuadro = (0, 255, 0)  # Verde
grosor_cuadro = 2
# --- Fin Configuración ---

# 1. Cargar el modelo DNN desde los archivos
try:
    net = cv2.dnn.readNetFromCaffe(prototxt_path, caffe_model_path)
except cv2.error as e:
    print(f"Error: No se pudieron cargar los archivos del modelo.")
    print(f"Asegúrate de tener 'deploy.prototxt.txt' y 'res10_300x300_ssd_iter_140000.caffemodel' en la carpeta.")
    exit()

# 2. Iniciar la captura de video
captura = cv2.VideoCapture(ruta_video)
if not captura.isOpened():
    print(f"Error: No se pudo abrir el video en {ruta_video}")
    exit()

print('Procesando video... Presiona "q" para salir.')

# 3. Bucle para procesar cada fotograma
while True:
    ret, frame = captura.read()
    if not ret:
        print("Video finalizado.")
        break

    # Obtener las dimensiones del fotograma
    (h, w) = frame.shape[:2]

    # 4. Pre-procesar el fotograma para el modelo DNN
    # Redimensiona a 300x300 y normaliza
    blob = cv2.dnn.blobFromImage(
        cv2.resize(frame, (300, 300)),  # Redimensiona la imagen
        1.0,  # Factor de escala (sin cambios)
        (300, 300),  # Tamaño final
        (104.0, 177.0, 123.0)  # Valores de sustracción media (BGR)
    )

    # 5. Pasar el 'blob' a la red y obtener las detecciones
    net.setInput(blob)
    detections = net.forward()

    # 6. Recorrer todas las detecciones encontradas
    # La forma de 'detections' es [1, 1, N, 7] donde N es el nro. de detecciones
    for i in range(0, detections.shape[2]):
        # Extraer la confianza (probabilidad) de la detección
        confidence = detections[0, 0, i, 2]

        # 7. Filtrar detecciones débiles (menores a confianza_minima)
        if confidence > confianza_minima:
            # 8. Calcular las coordenadas (x, y) del cuadro
            # Las coordenadas del modelo están normalizadas (0.0 a 1.0)
            # Hay que multiplicarlas por las dimensiones originales (h, w)
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            (startX, startY, endX, endY) = box.astype("int")

            # 9. Dibujar el cuadro verde
            cv2.rectangle(frame, (startX, startY), (endX, endY), color_cuadro, grosor_cuadro)

            # (Opcional) Dibujar la confianza sobre el cuadro
            texto = f"{confidence * 100:.2f}%"
            # Poner el texto un poco arriba del cuadro
            y = startY - 10 if startY - 10 > 10 else startY + 10
            cv2.putText(frame, texto, (startX, y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, color_cuadro, 2)

    # 10. Mostrar el fotograma resultante
    cv2.imshow('Deteccion DNN (Presiona "q")', frame)

    if cv2.waitKey(25) & 0xFF == ord('q'):
        break

# 11. Liberar recursos
captura.release()
cv2.destroyAllWindows()