from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

# Supón que la contraseña del supervisor es "supervisor1pass"
password = "supervisor1pass"

# Encriptar la contraseña
hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

# Aquí deberías guardar `hashed_password` en tu base de datos
print(f"Password hash: {hashed_password}")
