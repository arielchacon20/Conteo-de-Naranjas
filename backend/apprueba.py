import cv2
import numpy as np
from pymongo import MongoClient

# Configura la conexión a MongoDB
client = MongoClient("mongodb+srv://desarrollo2023:rFtSer5m5UVVuoYI@millenium.pardqk8.mongodb.net/")
db = client["frutas_contador"]
collection = db["conteo_naranjas"]
errores_collection = db["errores"]

# Inicializa el contador de naranjas
contador_naranjas = 0
naranja_presente = False
detencion = False
producto_mal_estado = False

# Función para obtener el siguiente ID de conteo
def obtener_siguiente_id():
    ultimo_conteo = collection.find_one(sort=[("_id", -1)])
    if ultimo_conteo:
        return int(ultimo_conteo["_id"]) + 1
    else:
        return 1

# Solicita información de nombre y proveedor
def obtener_datos_conteo():
    nombre_conteo = input("Ingrese su nombre: ")
    proveedor = input("Ingrese el nombre del proveedor: ")
    return nombre_conteo, proveedor

# Función para detectar el color naranja y contar
def detectar_color_naranja():
    global contador_naranjas, naranja_presente, detencion, producto_mal_estado

    # Solicitar nombre y proveedor antes de iniciar el conteo
    nombre_supervisor, proveedor = obtener_datos_conteo()
    siguiente_id = obtener_siguiente_id()

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: No se pudo abrir la cámara.")
        return

    while True:
        if detencion or producto_mal_estado:
            # Mostrar mensaje de detención en pantalla
            mensaje = "Pausado. Presiona 's' para reanudar" if detencion else "Producto en mal estado. Proceso detenido"
            cv2.putText(frame, mensaje, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            cv2.imshow("Frame Original", frame)
            if cv2.waitKey(1) & 0xFF == ord('s'):
                detencion = False
                producto_mal_estado = False
            continue

        ret, frame = cap.read()
        if not ret:
            print("Error: No se pudo leer el frame.")
            break

        # Convertir el frame de BGR a HSV
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Definir el rango de color naranja en HSV
        lower_orange = np.array([10, 100, 100])
        upper_orange = np.array([25, 255, 255])

        # Crear máscara para el rango de naranja
        mask_orange = cv2.inRange(hsv, lower_orange, upper_orange)
        mask_orange = cv2.GaussianBlur(mask_orange, (5, 5), 0)

        # Definir rangos para manchas negras y blancas en HSV
        lower_black = np.array([0, 0, 0])
        upper_black = np.array([180, 255, 30])
        lower_white = np.array([0, 0, 200])
        upper_white = np.array([180, 20, 255])

        # Crear máscaras para manchas negras y blancas
        mask_black = cv2.inRange(hsv, lower_black, upper_black)
        #mask_white = cv2.inRange(hsv, lower_white, upper_white)

        # Dibujar un cuadro en el centro como área de detección
        height, width, _ = frame.shape
        area_x1, area_y1 = int(width * 0.4), int(height * 0.4)
        area_x2, area_y2 = int(width * 0.6), int(height * 0.6)
        cv2.rectangle(frame, (area_x1, area_y1), (area_x2, area_y2), (255, 0, 0), 2)

        # Encontrar contornos en la máscara de naranja
        contours, _ = cv2.findContours(mask_orange, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        naranja_detectada = False
        manchas_detectadas = False

        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 500:
                x, y, w, h = cv2.boundingRect(contour)
                if area_x1 < x + w // 2 < area_x2 and area_y1 < y + h // 2 < area_y2:
                    naranja_detectada = True
                    cv2.drawContours(frame, [contour], -1, (0, 255, 0), 2)
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

                    # Verificar si hay manchas negras o blancas en el área de la naranja
                    if cv2.countNonZero(mask_black[y:y+h, x:x+w]) > 50 :
                        manchas_detectadas = True
                        break

        # Lógica de conteo y detección de mal estado
        if manchas_detectadas:
            producto_mal_estado = True
            print("Producto en mal estado detectado.")
            cv2.putText(frame, "Producto en mal estado", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            cv2.putText(frame, "s", (width // 2, height // 2), cv2.FONT_HERSHEY_SIMPLEX, 5, (0, 0, 255), 10)

                    # Guardar el registro en la colección de errores
            errores_collection.insert_one({
                "_id": siguiente_id,
                "nombre_supervisor": nombre_supervisor,
                "proveedor": proveedor,
                "mensaje": "Producto en mal estado, revisión del proveedor"
            })
            # Pausar el sistema y verificar
            while True:
                cv2.putText(frame, "Presione 'd' para eliminar error o 'c' para continuar", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                cv2.imshow("Frame Original", frame)
                key = cv2.waitKey(0) & 0xFF

                if key == ord('d'):
                    # Eliminar el registro de errores si se confirma que el mal estado es un error
                    errores_collection.delete_one({"_id": siguiente_id})
                    print("Error eliminado. Continuando...")
                    producto_mal_estado = False
                    break
                elif key == ord('c'):
                    # Continuar sin eliminar el error
                    print("Continuando con el error registrado.")
                    break

        elif naranja_detectada and not naranja_presente:
            contador_naranjas += 1
            naranja_presente = True
            collection.update_one(
                {"_id": siguiente_id},
                {"$set": {
                    "nombre_supervisor": nombre_supervisor,
                    "proveedor": proveedor,
                    "contador": contador_naranjas
                }},
                upsert=True
            )
            print(f"Naranja contada. Total: {contador_naranjas}")

        elif not naranja_detectada and naranja_presente:
            naranja_presente = False

        cv2.imshow("Frame Original", frame)
        cv2.imshow("Máscara Naranja", mask_orange)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('s'):
            detencion = not detencion
            print("Sistema en pausa." if detencion else "Sistema reanudado.")
        if key == ord('q'):
            print("Sistema detenido.")
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    detectar_color_naranja()
