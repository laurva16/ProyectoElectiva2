# wsgi.py
# Punto de entrada para Gunicorn y AWS Lambda (Zappa)

import os
import sys
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Importar la aplicación Flask
from server import app

# Configurar según el entorno
if __name__ == "__main__":
    # Entorno local
    PORT = int(os.getenv("PORT", 5000))
    DEBUG = os.getenv("FLASK_ENV") == "development"
    
    print("=" * 60)
    print("🚀 Iniciando CineMax API")
    print("=" * 60)
    print(f"Entorno: {os.getenv('FLASK_ENV', 'development')}")
    print(f"Debug: {DEBUG}")
    print(f"Puerto: {PORT}")
    print(f"Base de datos: {os.getenv('DATABASE_NAME', 'cinemax_db')}")
    print("=" * 60)
    
    app.run(host="0.0.0.0", port=PORT, debug=DEBUG)

# Para AWS Lambda/Zappa
# El objeto 'app' será usado automáticamente por Lambda