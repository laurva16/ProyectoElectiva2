# config.py
import os

MONGODB_URI = os.getenv(
    "MONGODB_URI",
    "mongodb+srv://brayanlopez07_db_user:og4ofPGbUK4WWwST@cinemaxcluster.7mrkjdk.mongodb.net/?retryWrites=true&w=majority&appName=CineMaxCluster"
)

DATABASE_NAME = os.getenv("DATABASE_NAME", "cinemax_db")
JWT_SECRET = os.getenv("JWT_SECRET", "tu_clave_secreta_super_segura_2024")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
FLASK_ENV = os.getenv("FLASK_ENV", "development")
DEBUG = FLASK_ENV == "development"
PORT = int(os.getenv("PORT", 5000))

# CORS - Simplificado para Lambda
ALLOWED_ORIGINS = ["*"]