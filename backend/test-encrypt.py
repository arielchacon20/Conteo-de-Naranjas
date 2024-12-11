from flask_bcrypt import Bcrypt
import cv2
import numpy as np
from pymongo import MongoClient
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_bcrypt import Bcrypt
import hashlib

# Inicializar Flask, MongoDB y Bcrypt
app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Asegúrate de cambiar esto a algo más seguro
bcrypt = Bcrypt(app)

# Configura la conexión a MongoDB
client = MongoClient("mongodb+srv://desarrollo2023:rFtSer5m5UVVuoYI@millenium.pardqk8.mongodb.net/")
db = client["frutas_contador"]
users_collection = db["users"]
conteo_naranjas_collection = db["conteo_naranjas"]
errores_collection = db["errores"]

bcrypt = Bcrypt()

# Suponiendo que obtienes el nombre de usuario y la contraseña del formulario
username = "supervisor1"
password = "supervisor1pass"  # Contraseña que el usuario ingresa

# Buscar al usuario en la base de datos (MongoDB)
user = db.users.find_one({"username": username})

# Verificar que el usuario existe y que la contraseña es correcta
if user and bcrypt.check_password_hash(user["password"], password):
    print("Login exitoso")
else:
    print("Login fallido")
