# database.py
# Gestión de la conexión a MongoDB Atlas

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from config import MONGODB_URI, DATABASE_NAME
import sys

class MongoDB:
    """Clase para gestionar la conexión a MongoDB Atlas"""
    
    def __init__(self):
        self.client = None
        self.db = None
        self.connect()
    
    def connect(self):
        """Establecer conexión con MongoDB Atlas"""
        try:
            print("🔄 Conectando a MongoDB Atlas...")
            
            # Crear cliente de MongoDB
            self.client = MongoClient(
                MONGODB_URI,
                serverSelectionTimeoutMS=5000,  # Timeout de 5 segundos
                connectTimeoutMS=10000
            )
            
            # Verificar conexión
            self.client.admin.command('ping')
            
            # Seleccionar base de datos
            self.db = self.client[DATABASE_NAME]
            
            print("✅ Conectado exitosamente a MongoDB Atlas")
            print(f"📦 Base de datos: {DATABASE_NAME}")
            
            # Inicializar colecciones si no existen
            self._initialize_collections()
            
        except ConnectionFailure as e:
            print(f"❌ Error de conexión a MongoDB: {e}")
            sys.exit(1)
        except ServerSelectionTimeoutError as e:
            print(f"❌ No se pudo conectar al servidor MongoDB: {e}")
            print("⚠️  Verifica:")
            print("   - Tu conexión a internet")
            print("   - Que tu IP esté en la lista blanca de MongoDB Atlas")
            print("   - Que el connection string sea correcto")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Error inesperado: {e}")
            sys.exit(1)
    
    def _initialize_collections(self):
        """Crear colecciones y datos iniciales si no existen"""
        
        # Colecciones necesarias
        collections = ['usuarios', 'peliculas', 'salas', 'tickets', 'reportes']
        
        existing_collections = self.db.list_collection_names()
        
        for collection in collections:
            if collection not in existing_collections:
                self.db.create_collection(collection)
                print(f"📝 Colección '{collection}' creada")
        
        # Insertar usuarios iniciales si no existen
        if self.db.usuarios.count_documents({}) == 0:
            usuarios_iniciales = [
                {
                    "id": 1,
                    "email": "admin@cinemax.com",
                    "password": "admin123",
                    "name": "Administrador Principal",
                    "role": "admin",
                    "telefono": "+57 300 1234567",
                    "direccion": "Calle Principal 123",
                    "permissions": ["all"]
                },
                {
                    "id": 2,
                    "email": "cliente@cinemax.com",
                    "password": "cliente123",
                    "name": "Juan Pérez",
                    "role": "cliente",
                    "telefono": "+57 310 9876543",
                    "direccion": "Carrera 45 #12-34",
                    "permissions": ["read", "buy_tickets"]
                },
                {
                    "id": 3,
                    "email": "cajero@cinemax.com",
                    "password": "cajero123",
                    "name": "María García",
                    "role": "cajero",
                    "telefono": "+57 320 5551234",
                    "direccion": "Avenida 68 #23-45",
                    "permissions": ["read", "create_tickets"]
                }
            ]
            self.db.usuarios.insert_many(usuarios_iniciales)
            print("👥 Usuarios iniciales creados")
        
        # Insertar películas iniciales si no existen
        if self.db.peliculas.count_documents({}) == 0:
            peliculas_iniciales = [
                {
                    "id": 1,
                    "titulo": "Spider-Man: Across the Spider-Verse",
                    "descripcion": "Miles Morales se adentra en el Multiverso.",
                    "duracion": 140,
                    "genero": "Animación",
                    "clasificacion": "PG-13",
                    "director": "Joaquim Dos Santos",
                    "actores": "Shameik Moore, Hailee Steinfeld",
                    "imagen_url": "https://image.tmdb.org/t/p/w500/gh4cZbhZxyTbgxQPxD0dOudNPTn.jpg",
                    "estado": "cartelera",
                    "precio": 12.99
                },
                {
                    "id": 2,
                    "titulo": "The Flash",
                    "descripcion": "Barry Allen usa sus superpoderes para viajar en el tiempo.",
                    "duracion": 144,
                    "genero": "Acción",
                    "clasificacion": "PG-13",
                    "director": "Andy Muschietti",
                    "actores": "Ezra Miller, Michael Keaton",
                    "imagen_url": "https://image.tmdb.org/t/p/w500/rktDFPbfHfUbArZ6OOOKsXcv0Bm.jpg",
                    "estado": "cartelera",
                    "precio": 13.99
                },
                {
                    "id": 3,
                    "titulo": "Elemental",
                    "descripcion": "En una ciudad donde los elementos viven juntos.",
                    "duracion": 109,
                    "genero": "Animación",
                    "clasificacion": "PG",
                    "director": "Peter Sohn",
                    "actores": "Leah Lewis, Mamoudou Athie",
                    "imagen_url": "https://image.tmdb.org/t/p/w500/6oH378KUfCEitzJkm07r97L0RsZ.jpg",
                    "estado": "cartelera",
                    "precio": 11.99
                },
                {
                    "id": 4,
                    "titulo": "Interstellar",
                    "descripcion": "Un grupo de exploradores hace uso de un agujero de gusano.",
                    "duracion": 169,
                    "genero": "Ciencia Ficción",
                    "clasificacion": "PG-13",
                    "director": "Christopher Nolan",
                    "actores": "Matthew McConaughey, Anne Hathaway",
                    "imagen_url": "https://image.tmdb.org/t/p/w500/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg",
                    "estado": "disponible",
                    "precio": 9.99
                }
            ]
            self.db.peliculas.insert_many(peliculas_iniciales)
            print("🎬 Películas iniciales creadas")
    
    def get_collection(self, collection_name):
        """Obtener una colección de la base de datos"""
        return self.db[collection_name]
    
    def close(self):
        """Cerrar la conexión"""
        if self.client:
            self.client.close()
            print("🔌 Conexión a MongoDB cerrada")


# Instancia global de MongoDB
mongodb = MongoDB()

# Acceso rápido a colecciones
usuarios_collection = mongodb.get_collection('usuarios')
peliculas_collection = mongodb.get_collection('peliculas')
salas_collection = mongodb.get_collection('salas')
tickets_collection = mongodb.get_collection('tickets')
reportes_collection = mongodb.get_collection('reportes')