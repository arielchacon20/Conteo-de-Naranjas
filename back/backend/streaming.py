from flask import Response
from image_processing import detectar_color_naranja
from db_handler import obtener_siguiente_id 

import cv2

cap = cv2.VideoCapture(0)

def generar_frames():
    nombre_supervisor = "Supervisor"  # Obtener desde el frontend
    proveedor = "Proveedor"          # Obtener desde el frontend
    siguiente_id = obtener_siguiente_id()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame, mask, total = detectar_color_naranja(frame, siguiente_id, nombre_supervisor, proveedor)

        _, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
