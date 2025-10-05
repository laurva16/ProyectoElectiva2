# usuarios.py
# Módulo de gestión de usuarios/clientes con MongoDB

from flask import Blueprint, request, jsonify
from functools import wraps
import jwt
from config import JWT_SECRET, JWT_ALGORITHM
from models import Usuario
from datetime import datetime

usuarios_bp = Blueprint('usuarios', __name__, url_prefix='/api/usuarios')


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


@usuarios_bp.route('', methods=['GET'])
@admin_required
def get_usuarios():
    """Obtener todos los usuarios (solo admin)"""
    try:
        rol = request.args.get('rol', None)
        busqueda = request.args.get('q', None)
        
        usuarios = Usuario.get_all()
        
        if rol:
            usuarios = [u for u in usuarios if u['role'].lower() == rol.lower()]
        
        if busqueda:
            busqueda = busqueda.lower()
            usuarios = [
                u for u in usuarios 
                if busqueda in u['name'].lower() or busqueda in u['email'].lower()
            ]
        
        for usuario in usuarios:
            usuario.pop('password', None)
        
        return jsonify({
            'success': True,
            'message': 'Usuarios obtenidos exitosamente',
            'data': usuarios,
            'count': len(usuarios)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al obtener usuarios: {str(e)}'
        }), 500


@usuarios_bp.route('/<int:usuario_id>', methods=['GET'])
@admin_required
def get_usuario(usuario_id):
    """Obtener un usuario por ID"""
    try:
        usuario = Usuario.find_by_id(usuario_id)
        
        if not usuario:
            return jsonify({
                'success': False,
                'message': 'Usuario no encontrado'
            }), 404
        
        # Crear una copia para no modificar el original
        usuario_data = dict(usuario)
        usuario_data.pop('password', None)
        usuario_data.pop('_id', None)
        
        return jsonify({
            'success': True,
            'message': 'Usuario obtenido exitosamente',
            'data': usuario_data
        }), 200
        
    except Exception as e:
        print(f"Error al obtener usuario {usuario_id}: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error al obtener usuario: {str(e)}'
        }), 500


@usuarios_bp.route('', methods=['POST'])
@admin_required
def create_usuario():
    """Crear un nuevo usuario (solo admin)"""
    try:
        data = request.get_json()
        
        required_fields = ['email', 'password', 'name', 'role']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'El campo {field} es requerido'
                }), 400
        
        email = data['email']
        if '@' not in email or '.' not in email:
            return jsonify({
                'success': False,
                'message': 'Formato de email inválido'
            }), 400
        
        if Usuario.find_by_email(email):
            return jsonify({
                'success': False,
                'message': 'El email ya está registrado'
            }), 409
        
        roles_validos = ['admin', 'cliente', 'cajero']
        if data['role'] not in roles_validos:
            return jsonify({
                'success': False,
                'message': f'Rol inválido. Debe ser uno de: {", ".join(roles_validos)}'
            }), 400
        
        if len(data['password']) < 6:
            return jsonify({
                'success': False,
                'message': 'La contraseña debe tener al menos 6 caracteres'
            }), 400
        
        nuevo_usuario = Usuario.create(
            email=data['email'],
            password=data['password'],
            name=data['name'],
            role=data['role'],
            telefono=data.get('telefono', ''),
            direccion=data.get('direccion', '')
        )
        
        if not nuevo_usuario:
            return jsonify({
                'success': False,
                'message': 'Error al crear usuario'
            }), 500
        
        nuevo_usuario.pop('password', None)
        
        return jsonify({
            'success': True,
            'message': 'Usuario creado exitosamente',
            'data': nuevo_usuario
        }), 201
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al crear usuario: {str(e)}'
        }), 500


@usuarios_bp.route('/<int:usuario_id>', methods=['PUT', 'PATCH'])
@admin_required
def update_usuario(usuario_id):
    """Actualizar un usuario"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No se enviaron datos para actualizar'
            }), 400
        
        usuario_existente = Usuario.find_by_id(usuario_id)
        if not usuario_existente:
            return jsonify({
                'success': False,
                'message': 'Usuario no encontrado'
            }), 404
        
        if 'email' in data and data['email'] != usuario_existente['email']:
            if Usuario.find_by_email(data['email']):
                return jsonify({
                    'success': False,
                    'message': 'El email ya está en uso por otro usuario'
                }), 409
        
        if 'role' in data:
            roles_validos = ['admin', 'cliente', 'cajero']
            if data['role'] not in roles_validos:
                return jsonify({
                    'success': False,
                    'message': f'Rol inválido. Debe ser uno de: {", ".join(roles_validos)}'
                }), 400
        
        if 'password' in data and len(data['password']) < 6:
            return jsonify({
                'success': False,
                'message': 'La contraseña debe tener al menos 6 caracteres'
            }), 400
        
        usuario_actualizado = Usuario.update(usuario_id, data)
        
        if not usuario_actualizado:
            return jsonify({
                'success': False,
                'message': 'Error al actualizar usuario'
            }), 500
        
        usuario_actualizado.pop('password', None)
        
        return jsonify({
            'success': True,
            'message': 'Usuario actualizado exitosamente',
            'data': usuario_actualizado
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al actualizar usuario: {str(e)}'
        }), 500


@usuarios_bp.route('/<int:usuario_id>', methods=['DELETE'])
@admin_required
def delete_usuario(usuario_id):
    """Eliminar un usuario"""
    try:
        if request.current_user['user_id'] == usuario_id:
            return jsonify({
                'success': False,
                'message': 'No puedes eliminar tu propia cuenta'
            }), 400
        
        usuario = Usuario.find_by_id(usuario_id)
        if not usuario:
            return jsonify({
                'success': False,
                'message': 'Usuario no encontrado'
            }), 404
        
        success = Usuario.delete(usuario_id)
        
        if not success:
            return jsonify({
                'success': False,
                'message': 'Error al eliminar usuario'
            }), 500
        
        return jsonify({
            'success': True,
            'message': 'Usuario eliminado exitosamente'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al eliminar usuario: {str(e)}'
        }), 500


@usuarios_bp.route('/stats', methods=['GET'])
@admin_required
def get_usuarios_stats():
    """Obtener estadísticas de usuarios"""
    try:
        usuarios = Usuario.get_all()
        
        total = len(usuarios)
        por_rol = {}
        
        for u in usuarios:
            rol = u['role']
            por_rol[rol] = por_rol.get(rol, 0) + 1
        
        return jsonify({
            'success': True,
            'message': 'Estadísticas obtenidas exitosamente',
            'data': {
                'total': total,
                'por_rol': por_rol,
                'clientes': por_rol.get('cliente', 0),
                'admins': por_rol.get('admin', 0),
                'cajeros': por_rol.get('cajero', 0)
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al obtener estadísticas: {str(e)}'
        }), 500