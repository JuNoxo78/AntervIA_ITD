import cv2

# --- Configuración ---
# Ruta al archivo XML de Haar Cascade
ruta_clasificador = '../resources/haarcascade_frontalface_default.xml'

# ¡AQUÍ ESTÁ EL CAMBIO!
# En lugar de 0, pones el nombre de tu archivo de video
ruta_video = 0

# Configuración del cuadro
color_cuadro = (0, 255, 0) # Verde en BGR
grosor_cuadro = 2
# --- Fin Configuración ---

# 1. Cargar el clasificador
clasificador_rostros = cv2.CascadeClassifier(ruta_clasificador)

# 2. Iniciar la captura de video DESDE UN ARCHIVO
captura = cv2.VideoCapture(ruta_video)

# Verificar si el video se abrió correctamente
if not captura.isOpened():
    print(f"Error: No se pudo abrir el archivo de video en {ruta_video}")
    exit()

# 3. Bucle para procesar cada fotograma del video
while True:
    ret, frame = captura.read()

    if not ret:
        print("Video finalizado o error al leer.")
        break

    frame_gris = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # 5. Detectar rostros
    rostros_detectados = clasificador_rostros.detectMultiScale(
        frame_gris,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30)
    )

    # 6. Dibujar rectángulos en el fotograma original (a color)
    for (x, y, w, h) in rostros_detectados:
        cv2.rectangle(frame, (x, y), (x + w, y + h), color_cuadro, grosor_cuadro)

    # 7. Mostrar el fotograma resultante
    cv2.imshow('Deteccion en Video (Presiona "d" para salir)', frame)

    if cv2.waitKey(20) & 0xFF == ord('d'):
        break

captura.release()
cv2.destroyAllWindows()