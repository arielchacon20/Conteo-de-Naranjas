from pymongo import MongoClient

# Configura la conexión a MongoDB
client = MongoClient("mongodb+srv://desarrollo2023:rFtSer5m5UVVuoYI@millenium.pardqk8.mongodb.net/")
db = client["frutas_contador"]
collection = db["conteo_naranjas"]
errores_collection = db["errores"]

def obtener_siguiente_id():
    """Obtiene el siguiente ID de conteo"""
    ultimo_conteo = collection.find_one(sort=[("_id", -1)])
    return int(ultimo_conteo["_id"]) + 1 if ultimo_conteo else 1

def registrar_error(siguiente_id, nombre_supervisor, proveedor, mensaje):
    """Registra un error en la colección de errores"""
    errores_collection.insert_one({
        "_id": siguiente_id,
        "nombre_supervisor": nombre_supervisor,
        "proveedor": proveedor,
        "mensaje": mensaje
    })

def registrar_conteo(siguiente_id, nombre_supervisor, proveedor, contador_naranjas):
    """Actualiza o inserta el conteo de naranjas"""
    collection.update_one(
        {"_id": siguiente_id},
        {"$set": {
            "nombre_supervisor": nombre_supervisor,
            "proveedor": proveedor,
            "contador": contador_naranjas
        }},
        upsert=True
    )

def get_fruit_counts():
    """Obtiene el conteo de frutas (en este caso naranjas)"""
    try:
        # Obtenemos el último conteo registrado en la colección 'conteo_naranjas'
        ultimo_conteo = collection.find_one(sort=[("_id", -1)])

        # Si no hay registros, devolvemos un conteo vacío
        if not ultimo_conteo:
            return {"naranjas": 0}

        # Extraemos el contador de naranjas
        contador_naranjas = ultimo_conteo.get("contador", 0)

        return {"naranjas": contador_naranjas}
    except Exception as e:
        print(f"Error al obtener el conteo de frutas: {e}")
        return {"naranjas": 0}

