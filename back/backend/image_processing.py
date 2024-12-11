import cv2
import numpy as np
from db_handler import registrar_error, registrar_conteo, obtener_siguiente_id

contador_naranjas = 0
naranja_presente = False

def detectar_color_naranja(frame, siguiente_id, nombre_supervisor, proveedor):
    """Procesa el frame para detectar naranjas y contar"""
    global contador_naranjas, naranja_presente

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Definir el rango de color naranja en HSV
    lower_orange = np.array([10, 100, 100])
    upper_orange = np.array([25, 255, 255])

    mask_orange = cv2.inRange(hsv, lower_orange, upper_orange)
    contours, _ = cv2.findContours(mask_orange, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    naranja_detectada = False
    for contour in contours:
        if cv2.contourArea(contour) > 500:
            naranja_detectada = True
            break

    if naranja_detectada and not naranja_presente:
        contador_naranjas += 1
        naranja_presente = True
        registrar_conteo(siguiente_id, nombre_supervisor, proveedor, contador_naranjas)

    elif not naranja_detectada and naranja_presente:
        naranja_presente = False

    return frame, mask_orange, contador_naranjas
