# models.py
# Modelos de datos para la aplicación CineMax

from datetime import datetime
from typing import List, Dict, Optional

class Usuario:
    """Modelo de Usuario"""
    def __init__(self, id: int, email: str, password: str, name: str, 
                 role: str = "employee", permissions: List[str] = None):
        self.id = id
        self.email = email
        self.password = password
        self.name = name
        self.role = role
        self.permissions = permissions or (["all"] if role == "admin" else ["read"])
    
    def to_dict(self, include_password: bool = False):
        """Convierte el usuario a diccionario"""
        user_dict = {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "role": self.role,
            "permissions": self.permissions
        }
        if include_password:
            user_dict["password"] = self.password
        return user_dict


class Pelicula:
    """Modelo de Película"""
    def __init__(self, id: Optional[int], titulo: str, descripcion: str, 
                 duracion: int, genero: str, clasificacion: str,
                 director: str = "", actores: str = "",
                 imagen_url: str = "", trailer_url: str = "",
                 fecha_estreno: str = "", estado: str = "disponible",
                 precio: float = 0.0):
        self.id = id
        self.titulo = titulo
        self.descripcion = descripcion
        self.duracion = duracion
        self.genero = genero
        self.clasificacion = clasificacion
        self.director = director
        self.actores = actores
        self.imagen_url = imagen_url
        self.trailer_url = trailer_url
        self.fecha_estreno = fecha_estreno or datetime.now().strftime("%Y-%m-%d")
        self.estado = estado
        self.precio = precio
        self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
    
    def to_dict(self):
        """Convierte la película a diccionario"""
        return {
            "id": self.id,
            "titulo": self.titulo,
            "descripcion": self.descripcion,
            "duracion": self.duracion,
            "genero": self.genero,
            "clasificacion": self.clasificacion,
            "director": self.director,
            "actores": self.actores,
            "imagen_url": self.imagen_url,
            "trailer_url": self.trailer_url,
            "fecha_estreno": self.fecha_estreno,
            "estado": self.estado,
            "precio": self.precio,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    def update(self, data: Dict):
        """Actualiza los campos de la película"""
        for key, value in data.items():
            if hasattr(self, key) and key != 'id':
                setattr(self, key, value)
        self.updated_at = datetime.now().isoformat()


# Base de datos en memoria (simulada)
class Database:
    """Clase para simular una base de datos"""
    
    def __init__(self):
        self.usuarios = [
            Usuario(1, "admin@cinemax.com", "admin123", "Administrador", "admin"),
            Usuario(2, "empleado@cinemax.com", "emp123", "Empleado", "employee")
        ]
        
        self.peliculas = [
            Pelicula(
                id=1,
                titulo="Spider-Man: Across the Spider-Verse",
                descripcion="Miles Morales se adentra en el Multiverso, donde se encuentra con un equipo de Spider-People encargados de proteger su propia existencia. Cuando los héroes chocan sobre cómo manejar una nueva amenaza, Miles se enfrenta a los demás Spiders y redefine lo que significa ser un héroe para poder salvar a las personas que ama.",
                duracion=140,
                genero="Animación",
                clasificacion="PG-13",
                director="Joaquim Dos Santos",
                actores="Shameik Moore, Hailee Steinfeld",
                imagen_url="https://image.tmdb.org/t/p/w500/gh4cZbhZxyTbgxQPxD0dOudNPTn.jpg",  # ✅ Imagen correcta
                estado="cartelera",
                precio=12.99
            ),

            Pelicula(
                id=2,
                titulo="The Flash",
                descripcion="Barry Allen usa sus superpoderes para viajar en el tiempo y cambiar los eventos del pasado.",
                duracion=144,
                genero="Acción",
                clasificacion="PG-13",
                director="Andy Muschietti",
                actores="Ezra Miller, Michael Keaton",
                imagen_url="https://image.tmdb.org/t/p/w500/rktDFPbfHfUbArZ6OOOKsXcv0Bm.jpg",
                estado="cartelera",
                precio=13.99
            ),
            Pelicula(
                id=3,
                titulo="Elemental",
                descripcion="En una ciudad donde los elementos fuego, agua, tierra y aire viven juntos, una joven de fuego y un chico relajado de agua descubren algo elemental.",
                duracion=109,
                genero="Animación",
                clasificacion="PG",
                director="Peter Sohn",
                actores="Leah Lewis, Mamoudou Athie",
                imagen_url="https://image.tmdb.org/t/p/w500/6oH378KUfCEitzJkm07r97L0RsZ.jpg",
                estado="cartelera",
                precio=11.99
            ),
            Pelicula(
                id=4,
                titulo="Interstellar",
                descripcion="Un grupo de exploradores hace uso de un agujero de gusano recientemente descubierto para superar las limitaciones de los viajes espaciales.",
                duracion=169,
                genero="Ciencia Ficción",
                clasificacion="PG-13",
                director="Christopher Nolan",
                actores="Matthew McConaughey, Anne Hathaway",
                imagen_url="https://image.tmdb.org/t/p/w500/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg",
                estado="disponible",
                precio=9.99
            )
        ]
        
        self.next_pelicula_id = 5
    
    def get_all_usuarios(self):
        return [u.to_dict() for u in self.usuarios]
    
    def get_all_peliculas(self):
        return [p.to_dict() for p in self.peliculas]
    
    def get_pelicula_by_id(self, pelicula_id: int):
        pelicula = next((p for p in self.peliculas if p.id == pelicula_id), None)
        return pelicula.to_dict() if pelicula else None
    
    def create_pelicula(self, data: Dict):
        nueva_pelicula = Pelicula(
            id=self.next_pelicula_id,
            titulo=data.get('titulo'),
            descripcion=data.get('descripcion'),
            duracion=data.get('duracion'),
            genero=data.get('genero'),
            clasificacion=data.get('clasificacion'),
            director=data.get('director', ''),
            actores=data.get('actores', ''),
            imagen_url=data.get('imagen_url', ''),
            trailer_url=data.get('trailer_url', ''),
            fecha_estreno=data.get('fecha_estreno', ''),
            estado=data.get('estado', 'disponible'),
            precio=data.get('precio', 0.0)
        )
        self.peliculas.append(nueva_pelicula)
        self.next_pelicula_id += 1
        return nueva_pelicula.to_dict()
    
    def update_pelicula(self, pelicula_id: int, data: Dict):
        pelicula = next((p for p in self.peliculas if p.id == pelicula_id), None)
        if pelicula:
            pelicula.update(data)
            return pelicula.to_dict()
        return None
    
    def delete_pelicula(self, pelicula_id: int):
        pelicula = next((p for p in self.peliculas if p.id == pelicula_id), None)
        if pelicula:
            self.peliculas.remove(pelicula)
            return True
        return False


# Instancia global de la base de datos
db = Database()