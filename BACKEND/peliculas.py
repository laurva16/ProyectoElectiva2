# peliculas.py
# Módulo de gestión de películas

from flask import Blueprint, request, jsonify
from functools import wraps
import jwt

# Importar la configuración y base de datos
from models import db

# Configuración JWT (debe coincidir con server.py)
JWT_SECRET = "tu_clave_secreta_super_segura_2024"
JWT_ALGORITHM = "HS256"

# Crear Blueprint para las rutas de películas
peliculas_bp = Blueprint('peliculas', __name__, url_prefix='/api/peliculas')


def jwt_required(f):
    """Decorador para rutas que requieren autenticación JWT"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'success': False, 'message': 'Token mal formateado'}), 401
        
        if not token:
            return jsonify({'success': False, 'message': 'Token faltante'}), 401
        
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            request.current_user = payload
        except jwt.ExpiredSignatureError:
            return jsonify({'success': False, 'message': 'Token expirado'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'success': False, 'message': 'Token inválido'}), 401
        
        return f(*args, **kwargs)
    
    return decorated


def admin_required(f):
    """Decorador para rutas que requieren permisos de administrador"""
    @wraps(f)
    @jwt_required
    def decorated(*args, **kwargs):
        user_data = request.current_user
        if user_data.get('role') != 'admin':
            return jsonify({
                'success': False,
                'message': 'Se requieren permisos de administrador'
            }), 403
        return f(*args, **kwargs)
    
    return decorated


# =====================
# RUTAS DE PELÍCULAS
# =====================

@peliculas_bp.route('', methods=['GET'])
@jwt_required
def get_peliculas():
    """
    GET /api/peliculas
    Obtener todas las películas
    Requiere: Autenticación
    """
    try:
        # Obtener parámetros de filtrado opcionales
        genero = request.args.get('genero', None)
        estado = request.args.get('estado', None)
        busqueda = request.args.get('q', None)
        
        peliculas = db.get_all_peliculas()
        
        # Aplicar filtros si existen
        if genero:
            peliculas = [p for p in peliculas if p['genero'].lower() == genero.lower()]
        
        if estado:
            peliculas = [p for p in peliculas if p['estado'].lower() == estado.lower()]
        
        if busqueda:
            busqueda = busqueda.lower()
            peliculas = [
                p for p in peliculas 
                if busqueda in p['titulo'].lower() or busqueda in p['descripcion'].lower()
            ]
        
        return jsonify({
            'success': True,
            'message': 'Películas obtenidas exitosamente',
            'data': peliculas,
            'count': len(peliculas)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al obtener películas: {str(e)}'
        }), 500


@peliculas_bp.route('/<int:pelicula_id>', methods=['GET'])
@jwt_required
def get_pelicula(pelicula_id):
    """
    GET /api/peliculas/{id}
    Obtener una película por ID
    Requiere: Autenticación
    """
    try:
        pelicula = db.get_pelicula_by_id(pelicula_id)
        
        if not pelicula:
            return jsonify({
                'success': False,
                'message': 'Película no encontrada'
            }), 404
        
        return jsonify({
            'success': True,
            'message': 'Película obtenida exitosamente',
            'data': pelicula
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al obtener película: {str(e)}'
        }), 500


@peliculas_bp.route('', methods=['POST'])
@admin_required
def create_pelicula():
    """
    POST /api/peliculas
    Crear una nueva película
    Requiere: Autenticación + Rol Admin
    """
    try:
        data = request.get_json()
        
        # Validar campos requeridos
        required_fields = ['titulo', 'descripcion', 'duracion', 'genero', 'clasificacion']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'El campo {field} es requerido'
                }), 400
        
        # Validar duracion
        try:
            duracion = int(data['duracion'])
            if duracion <= 0:
                raise ValueError
        except (ValueError, TypeError):
            return jsonify({
                'success': False,
                'message': 'La duración debe ser un número positivo'
            }), 400
        
        # Validar precio si viene
        if 'precio' in data:
            try:
                precio = float(data['precio'])
                if precio < 0:
                    raise ValueError
            except (ValueError, TypeError):
                return jsonify({
                    'success': False,
                    'message': 'El precio debe ser un número válido'
                }), 400
        
        # Crear película
        nueva_pelicula = db.create_pelicula(data)
        
        return jsonify({
            'success': True,
            'message': 'Película creada exitosamente',
            'data': nueva_pelicula
        }), 201
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al crear película: {str(e)}'
        }), 500


@peliculas_bp.route('/<int:pelicula_id>', methods=['PUT', 'PATCH'])
@admin_required
def update_pelicula(pelicula_id):
    """
    PUT/PATCH /api/peliculas/{id}
    Actualizar una película
    Requiere: Autenticación + Rol Admin
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No se enviaron datos para actualizar'
            }), 400
        
        # Validar duracion si viene
        if 'duracion' in data:
            try:
                duracion = int(data['duracion'])
                if duracion <= 0:
                    raise ValueError
            except (ValueError, TypeError):
                return jsonify({
                    'success': False,
                    'message': 'La duración debe ser un número positivo'
                }), 400
        
        # Validar precio si viene
        if 'precio' in data:
            try:
                precio = float(data['precio'])
                if precio < 0:
                    raise ValueError
            except (ValueError, TypeError):
                return jsonify({
                    'success': False,
                    'message': 'El precio debe ser un número válido'
                }), 400
        
        # Actualizar película
        pelicula_actualizada = db.update_pelicula(pelicula_id, data)
        
        if not pelicula_actualizada:
            return jsonify({
                'success': False,
                'message': 'Película no encontrada'
            }), 404
        
        return jsonify({
            'success': True,
            'message': 'Película actualizada exitosamente',
            'data': pelicula_actualizada
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al actualizar película: {str(e)}'
        }), 500


@peliculas_bp.route('/<int:pelicula_id>', methods=['DELETE'])
@admin_required
def delete_pelicula(pelicula_id):
    """
    DELETE /api/peliculas/{id}
    Eliminar una película
    Requiere: Autenticación + Rol Admin
    """
    try:
        success = db.delete_pelicula(pelicula_id)
        
        if not success:
            return jsonify({
                'success': False,
                'message': 'Película no encontrada'
            }), 404
        
        return jsonify({
            'success': True,
            'message': 'Película eliminada exitosamente'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al eliminar película: {str(e)}'
        }), 500


@peliculas_bp.route('/stats', methods=['GET'])
@jwt_required
def get_peliculas_stats():
    """
    GET /api/peliculas/stats
    Obtener estadísticas de películas
    Requiere: Autenticación
    """
    try:
        peliculas = db.get_all_peliculas()
        
        total = len(peliculas)
        en_cartelera = len([p for p in peliculas if p['estado'] == 'cartelera'])
        disponibles = len([p for p in peliculas if p['estado'] == 'disponible'])
        
        # Contar por género
        generos = {}
        for p in peliculas:
            genero = p['genero']
            generos[genero] = generos.get(genero, 0) + 1
        
        return jsonify({
            'success': True,
            'message': 'Estadísticas obtenidas exitosamente',
            'data': {
                'total': total,
                'en_cartelera': en_cartelera,
                'disponibles': disponibles,
                'por_genero': generos
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al obtener estadísticas: {str(e)}'
        }), 500