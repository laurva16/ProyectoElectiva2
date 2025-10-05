# models.py
# Modelos de datos para CineMax con MongoDB

from datetime import datetime
from typing import Dict
from database import usuarios_collection, peliculas_collection


class Usuario:
    """Modelo de Usuario"""
    
    @staticmethod
    def find_by_email(email: str):
        """Buscar usuario por email"""
        return usuarios_collection.find_one({"email": email})
    
    @staticmethod
    def find_by_id(user_id: int):
        """Buscar usuario por ID"""
        return usuarios_collection.find_one({"id": user_id})
    
    @staticmethod
    def create(email: str, password: str, name: str, role: str = "cliente", telefono: str = "", direccion: str = ""):
        """Crear un nuevo usuario"""
        if Usuario.find_by_email(email):
            return None
        
        last_user = usuarios_collection.find_one(sort=[("id", -1)])
        next_id = (last_user['id'] + 1) if last_user else 1
        
        # Definir permisos según el rol
        if role == "admin":
            permissions = ["all"]
        elif role == "cajero":
            permissions = ["read", "create_tickets"]
        else:  # cliente
            permissions = ["read", "buy_tickets"]
        
        usuario = {
            "id": next_id,
            "email": email,
            "password": password,
            "name": name,
            "role": role,
            "telefono": telefono,
            "direccion": direccion,
            "permissions": permissions,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        result = usuarios_collection.insert_one(usuario)
        usuario['_id'] = str(result.inserted_id)
        return usuario
    
    @staticmethod
    def update(user_id: int, data: Dict):
        """Actualizar un usuario"""
        data['updated_at'] = datetime.now().isoformat()
        
        result = usuarios_collection.update_one(
            {"id": user_id},
            {"$set": data}
        )
        
        if result.modified_count > 0:
            return Usuario.find_by_id(user_id)
        return None
    
    @staticmethod
    def delete(user_id: int):
        """Eliminar un usuario"""
        result = usuarios_collection.delete_one({"id": user_id})
        return result.deleted_count > 0
    
    @staticmethod
    def get_all():
        """Obtener todos los usuarios"""
        usuarios = list(usuarios_collection.find())
        for u in usuarios:
            u['_id'] = str(u['_id'])
        return usuarios


class Pelicula:
    """Modelo de Película"""
    
    @staticmethod
    def find_by_id(pelicula_id: int):
        """Buscar película por ID"""
        pelicula = peliculas_collection.find_one({"id": pelicula_id})
        if pelicula:
            pelicula['_id'] = str(pelicula['_id'])
        return pelicula
    
    @staticmethod
    def get_all():
        """Obtener todas las películas"""
        peliculas = list(peliculas_collection.find())
        for p in peliculas:
            p['_id'] = str(p['_id'])
        return peliculas
    
    @staticmethod
    def create(data: Dict):
        """Crear una nueva película"""
        last_pelicula = peliculas_collection.find_one(sort=[("id", -1)])
        next_id = (last_pelicula['id'] + 1) if last_pelicula else 1
        
        pelicula = {
            "id": next_id,
            "titulo": data.get('titulo'),
            "descripcion": data.get('descripcion'),
            "duracion": data.get('duracion'),
            "genero": data.get('genero'),
            "clasificacion": data.get('clasificacion'),
            "director": data.get('director', ''),
            "actores": data.get('actores', ''),
            "imagen_url": data.get('imagen_url', ''),
            "trailer_url": data.get('trailer_url', ''),
            "fecha_estreno": data.get('fecha_estreno', datetime.now().strftime("%Y-%m-%d")),
            "estado": data.get('estado', 'disponible'),
            "precio": data.get('precio', 0.0),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        result = peliculas_collection.insert_one(pelicula)
        pelicula['_id'] = str(result.inserted_id)
        return pelicula
    
    @staticmethod
    def update(pelicula_id: int, data: Dict):
        """Actualizar una película"""
        data['updated_at'] = datetime.now().isoformat()
        
        result = peliculas_collection.update_one(
            {"id": pelicula_id},
            {"$set": data}
        )
        
        if result.modified_count > 0:
            return Pelicula.find_by_id(pelicula_id)
        return None
    
    @staticmethod
    def delete(pelicula_id: int):
        """Eliminar una película"""
        result = peliculas_collection.delete_one({"id": pelicula_id})
        return result.deleted_count > 0