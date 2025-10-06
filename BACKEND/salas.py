# salas.py
# Módulo de gestión de salas con MongoDB

from flask import Blueprint, request, jsonify
from functools import wraps
import jwt
from config import JWT_SECRET, JWT_ALGORITHM
from database import salas_collection
from datetime import datetime

salas_bp = Blueprint('salas', __name__, url_prefix='/api/salas')


def jwt_required(f):
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


class Sala:
    """Modelo de Sala"""
    
    @staticmethod
    def find_by_id(sala_id):
        sala = salas_collection.find_one({"id": sala_id})
        if sala:
            sala['_id'] = str(sala['_id'])
        return sala
    
    @staticmethod
    def get_all():
        salas = list(salas_collection.find())
        for s in salas:
            s['_id'] = str(s['_id'])
        return salas
    
    @staticmethod
    def create(data):
        last_sala = salas_collection.find_one(sort=[("id", -1)])
        next_id = (last_sala['id'] + 1) if last_sala else 1
        
        sala = {
            "id": next_id,
            "nombre": data.get('nombre'),
            "capacidad": data.get('capacidad'),
            "tipo": data.get('tipo', 'Estándar'),
            "tecnologia": data.get('tecnologia', '2D'),
            "estado": data.get('estado', 'activa'),
            "precio_base": data.get('precio_base', 10.0),
            "filas": data.get('filas', 10),
            "asientos_por_fila": data.get('asientos_por_fila', 15),
            "descripcion": data.get('descripcion', ''),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        result = salas_collection.insert_one(sala)
        sala['_id'] = str(result.inserted_id)
        return sala
    
    @staticmethod
    def update(sala_id, data):
        data['updated_at'] = datetime.now().isoformat()
        
        result = salas_collection.update_one(
            {"id": sala_id},
            {"$set": data}
        )
        
        if result.modified_count > 0:
            return Sala.find_by_id(sala_id)
        return None
    
    @staticmethod
    def delete(sala_id):
        result = salas_collection.delete_one({"id": sala_id})
        return result.deleted_count > 0


@salas_bp.route('', methods=['GET'])
@jwt_required
def get_salas():
    """Obtener todas las salas"""
    try:
        tipo = request.args.get('tipo', None)
        estado = request.args.get('estado', None)
        busqueda = request.args.get('q', None)
        
        salas = Sala.get_all()
        
        if tipo:
            salas = [s for s in salas if s['tipo'].lower() == tipo.lower()]
        
        if estado:
            salas = [s for s in salas if s['estado'].lower() == estado.lower()]
        
        if busqueda:
            busqueda = busqueda.lower()
            salas = [
                s for s in salas 
                if busqueda in s['nombre'].lower() or busqueda in s.get('descripcion', '').lower()
            ]
        
        return jsonify({
            'success': True,
            'message': 'Salas obtenidas exitosamente',
            'data': salas,
            'count': len(salas)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al obtener salas: {str(e)}'
        }), 500


@salas_bp.route('/<int:sala_id>', methods=['GET'])
@jwt_required
def get_sala(sala_id):
    """Obtener una sala por ID"""
    try:
        sala = Sala.find_by_id(sala_id)
        
        if not sala:
            return jsonify({
                'success': False,
                'message': 'Sala no encontrada'
            }), 404
        
        return jsonify({
            'success': True,
            'message': 'Sala obtenida exitosamente',
            'data': sala
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al obtener sala: {str(e)}'
        }), 500


@salas_bp.route('', methods=['POST'])
@admin_required
def create_sala():
    """Crear una nueva sala"""
    try:
        data = request.get_json()
        
        required_fields = ['nombre', 'capacidad', 'tipo']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'El campo {field} es requerido'
                }), 400
        
        # Validar capacidad
        try:
            capacidad = int(data['capacidad'])
            if capacidad <= 0:
                raise ValueError
        except (ValueError, TypeError):
            return jsonify({
                'success': False,
                'message': 'La capacidad debe ser un número positivo'
            }), 400
        
        # Validar precio base
        if 'precio_base' in data:
            try:
                precio = float(data['precio_base'])
                if precio < 0:
                    raise ValueError
            except (ValueError, TypeError):
                return jsonify({
                    'success': False,
                    'message': 'El precio debe ser un número válido'
                }), 400
        
        nueva_sala = Sala.create(data)
        
        return jsonify({
            'success': True,
            'message': 'Sala creada exitosamente',
            'data': nueva_sala
        }), 201
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al crear sala: {str(e)}'
        }), 500


@salas_bp.route('/<int:sala_id>', methods=['PUT', 'PATCH'])
@admin_required
def update_sala(sala_id):
    """Actualizar una sala"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No se enviaron datos para actualizar'
            }), 400
        
        if 'capacidad' in data:
            try:
                capacidad = int(data['capacidad'])
                if capacidad <= 0:
                    raise ValueError
            except (ValueError, TypeError):
                return jsonify({
                    'success': False,
                    'message': 'La capacidad debe ser un número positivo'
                }), 400
        
        if 'precio_base' in data:
            try:
                precio = float(data['precio_base'])
                if precio < 0:
                    raise ValueError
            except (ValueError, TypeError):
                return jsonify({
                    'success': False,
                    'message': 'El precio debe ser un número válido'
                }), 400
        
        sala_actualizada = Sala.update(sala_id, data)
        
        if not sala_actualizada:
            return jsonify({
                'success': False,
                'message': 'Sala no encontrada'
            }), 404
        
        return jsonify({
            'success': True,
            'message': 'Sala actualizada exitosamente',
            'data': sala_actualizada
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al actualizar sala: {str(e)}'
        }), 500


@salas_bp.route('/<int:sala_id>', methods=['DELETE'])
@admin_required
def delete_sala(sala_id):
    """Eliminar una sala"""
    try:
        success = Sala.delete(sala_id)
        
        if not success:
            return jsonify({
                'success': False,
                'message': 'Sala no encontrada'
            }), 404
        
        return jsonify({
            'success': True,
            'message': 'Sala eliminada exitosamente'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al eliminar sala: {str(e)}'
        }), 500


@salas_bp.route('/stats', methods=['GET'])
@jwt_required
def get_salas_stats():
    """Obtener estadísticas de salas"""
    try:
        salas = Sala.get_all()
        
        total = len(salas)
        activas = len([s for s in salas if s['estado'] == 'activa'])
        en_mantenimiento = len([s for s in salas if s['estado'] == 'mantenimiento'])
        capacidad_total = sum(s['capacidad'] for s in salas)
        
        tipos = {}
        for s in salas:
            tipo = s['tipo']
            tipos[tipo] = tipos.get(tipo, 0) + 1
        
        return jsonify({
            'success': True,
            'message': 'Estadísticas obtenidas exitosamente',
            'data': {
                'total': total,
                'activas': activas,
                'en_mantenimiento': en_mantenimiento,
                'capacidad_total': capacidad_total,
                'por_tipo': tipos
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al obtener estadísticas: {str(e)}'
        }), 500