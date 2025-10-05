# config.py
# Configuración de MongoDB Atlas

import os

# MongoDB Atlas Connection String
MONGODB_URI = "mongodb+srv://brayanlopez07_db_user:og4ofPGbUK4WWwST@cinemaxcluster.7mrkjdk.mongodb.net/?retryWrites=true&w=majority&appName=CineMaxCluster"

# Nombre de la base de datos
DATABASE_NAME = "cinemax_db"

# JWT Configuration
JWT_SECRET = "tu_clave_secreta_super_segura_2024"
JWT_ALGORITHM = "HS256"

# Flask Configuration
FLASK_ENV = os.getenv("FLASK_ENV", "development")
DEBUG = FLASK_ENV == "development"
PORT = 5000