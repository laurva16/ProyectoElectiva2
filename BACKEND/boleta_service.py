from datetime import datetime
from typing import List, Optional, Dict
import uuid


class Boleta:
    """Clase que representa una boleta de cine"""
    
    def __init__(
        self,
        tipo_boleta: str,
        sala: str,
        fecha_hora: datetime,
        pelicula: str,
        id_boleta: Optional[str] = None,
        precio: Optional[float] = None
    ):
        self.id_boleta = id_boleta or str(uuid.uuid4())
        self.tipo_boleta = tipo_boleta  # "2D" o "3D"
        self.sala = sala
        self.fecha_hora = fecha_hora
        self.pelicula = pelicula
        self.precio = precio or (15000 if tipo_boleta == "2D" else 20000)
    
    def to_dict(self) -> Dict:
        """Convierte la boleta a diccionario"""
        return {
            "id_boleta": self.id_boleta,
            "tipo_boleta": self.tipo_boleta,
            "sala": self.sala,
            "fecha_hora": self.fecha_hora.isoformat(),
            "pelicula": self.pelicula,
            "precio": self.precio
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Boleta':
        """Crea una boleta desde un diccionario"""
        fecha_hora_str = data["fecha_hora"]
        if isinstance(fecha_hora_str, str):
            fecha_hora = datetime.fromisoformat(fecha_hora_str.replace('Z', '+00:00'))
        else:
            fecha_hora = fecha_hora_str
            
        return cls(
            id_boleta=data.get("id_boleta"),
            tipo_boleta=data["tipo_boleta"],
            sala=data["sala"],
            fecha_hora=fecha_hora,
            pelicula=data["pelicula"],
            precio=data.get("precio")
        )
    
    def __repr__(self):
        return f"Boleta(id={self.id_boleta}, tipo={self.tipo_boleta}, pelicula={self.pelicula})"


class BoletaService:
    """Servicio para gestionar boletas de cine"""
    
    def __init__(self):
        self._boletas: Dict[str, Boleta] = {}
        self._initialize_sample_data()
    
    def _initialize_sample_data(self):
        """Inicializa datos de ejemplo para pruebas"""
        boletas_ejemplo = [
            {
                "tipo_boleta": "3D",
                "sala": "Sala 1",
                "fecha_hora": datetime(2025, 10, 5, 19, 30),
                "pelicula": "Avatar 3",
                "precio": 25000
            },
            {
                "tipo_boleta": "2D",
                "sala": "Sala 2",
                "fecha_hora": datetime(2025, 10, 5, 20, 0),
                "pelicula": "Oppenheimer",
                "precio": 15000
            },
            {
                "tipo_boleta": "3D",
                "sala": "Sala VIP",
                "fecha_hora": datetime(2025, 10, 6, 18, 0),
                "pelicula": "Dune: Parte 3",
                "precio": 30000
            },
            {
                "tipo_boleta": "2D",
                "sala": "Sala 3",
                "fecha_hora": datetime(2025, 10, 6, 21, 30),
                "pelicula": "The Batman",
                "precio": 15000
            },
            {
                "tipo_boleta": "3D",
                "sala": "Sala 1",
                "fecha_hora": datetime(2025, 10, 7, 16, 0),
                "pelicula": "Spider-Man: Beyond",
                "precio": 22000
            }
        ]
        
        for boleta_data in boletas_ejemplo:
            self.crear_boleta(**boleta_data)
        
        print(f"✅ {len(boletas_ejemplo)} boletas de prueba cargadas")
    
    def _initialize_sample_data(self):
        """Inicializa datos de ejemplo"""
        boletas_ejemplo = [
            {
                "tipo_boleta": "3D",
                "sala": "Sala 1",
                "fecha_hora": datetime(2025, 10, 5, 19, 30),
                "pelicula": "Avatar 3"
            },
            {
                "tipo_boleta": "2D",
                "sala": "Sala 2",
                "fecha_hora": datetime(2025, 10, 5, 20, 0),
                "pelicula": "Oppenheimer"
            },
            {
                "tipo_boleta": "3D",
                "sala": "Sala VIP",
                "fecha_hora": datetime(2025, 10, 6, 18, 0),
                "pelicula": "Dune: Parte 3"
            }
        ]
        
        for boleta_data in boletas_ejemplo:
            self.crear_boleta(**boleta_data)
    
    def crear_boleta(
        self,
        tipo_boleta: str,
        sala: str,
        fecha_hora: datetime,
        pelicula: str,
        precio: Optional[float] = None
    ) -> Boleta:
        """
        Crea una nueva boleta
        
        Args:
            tipo_boleta: Tipo de boleta ("2D" o "3D")
            sala: Número o nombre de la sala
            fecha_hora: Fecha y hora de la función
            pelicula: Nombre de la película
            precio: Precio de la boleta (opcional)
            
        Returns:
            Boleta creada
            
        Raises:
            ValueError: Si el tipo de boleta no es válido
        """
        if tipo_boleta not in ["2D", "3D"]:
            raise ValueError("El tipo de boleta debe ser '2D' o '3D'")
        
        boleta = Boleta(
            tipo_boleta=tipo_boleta,
            sala=sala,
            fecha_hora=fecha_hora,
            pelicula=pelicula,
            precio=precio
        )
        
        self._boletas[boleta.id_boleta] = boleta
        return boleta
    
    def obtener_boleta(self, id_boleta: str) -> Optional[Boleta]:
        """
        Obtiene una boleta por su ID
        
        Args:
            id_boleta: ID de la boleta
            
        Returns:
            Boleta si existe, None en caso contrario
        """
        return self._boletas.get(id_boleta)
    
    def listar_boletas(
        self,
        tipo_boleta: Optional[str] = None,
        sala: Optional[str] = None,
        pelicula: Optional[str] = None
    ) -> List[Boleta]:
        """
        Lista todas las boletas con filtros opcionales
        
        Args:
            tipo_boleta: Filtrar por tipo de boleta
            sala: Filtrar por sala
            pelicula: Filtrar por película
            
        Returns:
            Lista de boletas que cumplen los criterios
        """
        boletas = list(self._boletas.values())
        
        if tipo_boleta:
            boletas = [b for b in boletas if b.tipo_boleta == tipo_boleta]
        
        if sala:
            boletas = [b for b in boletas if b.sala == sala]
        
        if pelicula:
            boletas = [b for b in boletas if b.pelicula.lower() == pelicula.lower()]
        
        return boletas
    
    def actualizar_boleta(
        self,
        id_boleta: str,
        tipo_boleta: Optional[str] = None,
        sala: Optional[str] = None,
        fecha_hora: Optional[datetime] = None,
        pelicula: Optional[str] = None,
        precio: Optional[float] = None
    ) -> Optional[Boleta]:
        """
        Actualiza una boleta existente
        
        Args:
            id_boleta: ID de la boleta a actualizar
            tipo_boleta: Nuevo tipo de boleta (opcional)
            sala: Nueva sala (opcional)
            fecha_hora: Nueva fecha y hora (opcional)
            pelicula: Nueva película (opcional)
            precio: Nuevo precio (opcional)
            
        Returns:
            Boleta actualizada si existe, None en caso contrario
            
        Raises:
            ValueError: Si el tipo de boleta no es válido
        """
        boleta = self._boletas.get(id_boleta)
        
        if not boleta:
            return None
        
        if tipo_boleta is not None:
            if tipo_boleta not in ["2D", "3D"]:
                raise ValueError("El tipo de boleta debe ser '2D' o '3D'")
            boleta.tipo_boleta = tipo_boleta
        
        if sala is not None:
            boleta.sala = sala
        
        if fecha_hora is not None:
            boleta.fecha_hora = fecha_hora
        
        if pelicula is not None:
            boleta.pelicula = pelicula
        
        if precio is not None:
            boleta.precio = precio
        
        return boleta
    
    def eliminar_boleta(self, id_boleta: str) -> bool:
        """
        Elimina una boleta
        
        Args:
            id_boleta: ID de la boleta a eliminar
            
        Returns:
            True si se eliminó, False si no existía
        """
        if id_boleta in self._boletas:
            del self._boletas[id_boleta]
            return True
        return False
    
    def contar_boletas(self) -> int:
        """Retorna el número total de boletas"""
        return len(self._boletas)
    
    def obtener_boletas_por_fecha(self, fecha: datetime) -> List[Boleta]:
        """
        Obtiene todas las boletas para una fecha específica
        
        Args:
            fecha: Fecha a buscar
            
        Returns:
            Lista de boletas para esa fecha
        """
        return [
            b for b in self._boletas.values()
            if b.fecha_hora.date() == fecha.date()
        ]
    
    def obtener_estadisticas(self) -> Dict:
        """
        Obtiene estadísticas de las boletas
        
        Returns:
            Diccionario con estadísticas
        """
        boletas = list(self._boletas.values())
        
        return {
            "total_boletas": len(boletas),
            "boletas_2d": len([b for b in boletas if b.tipo_boleta == "2D"]),
            "boletas_3d": len([b for b in boletas if b.tipo_boleta == "3D"]),
            "ingresos_totales": sum(b.precio for b in boletas),
            "peliculas_unicas": len(set(b.pelicula for b in boletas))
        }