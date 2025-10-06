# tickets.py
# Módulo de gestión de tickets/boletos con MongoDB

from flask import Blueprint, request, jsonify
from functools import wraps
import jwt
from config import JWT_SECRET, JWT_ALGORITHM
from database import tickets_collection, peliculas_collection, salas_collection, usuarios_collection
from datetime import datetime

tickets_bp = Blueprint('tickets', __name__, url_prefix='/api/tickets')


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


def admin_or_cajero_required(f):
    @wraps(f)
    @jwt_required
    def decorated(*args, **kwargs):
        user_data = request.current_user
        if user_data.get('role') not in ['admin', 'cajero']:
            return jsonify({
                'success': False,
                'message': 'Se requieren permisos de administrador o cajero'
            }), 403
        return f(*args, **kwargs)
    
    return decorated


class Ticket:
    """Modelo de Ticket"""
    
    @staticmethod
    def find_by_id(ticket_id):
        ticket = tickets_collection.find_one({"id": ticket_id})
        if ticket:
            ticket['_id'] = str(ticket['_id'])
        return ticket
    
    @staticmethod
    def get_all():
        tickets = list(tickets_collection.find())
        for t in tickets:
            t['_id'] = str(t['_id'])
        return tickets
    
    @staticmethod
    def create(data):
        last_ticket = tickets_collection.find_one(sort=[("id", -1)])
        next_id = (last_ticket['id'] + 1) if last_ticket else 1
        
        ticket = {
            "id": next_id,
            "pelicula_id": data.get('pelicula_id'),
            "pelicula_nombre": data.get('pelicula_nombre'),
            "sala_id": data.get('sala_id'),
            "sala_nombre": data.get('sala_nombre'),
            "usuario_id": data.get('usuario_id'),
            "usuario_nombre": data.get('usuario_nombre'),
            "asiento": data.get('asiento'),
            "fecha_funcion": data.get('fecha_funcion'),
            "hora_funcion": data.get('hora_funcion'),
            "precio": data.get('precio'),
            "estado": data.get('estado', 'reservado'),
            "metodo_pago": data.get('metodo_pago', 'efectivo'),
            "codigo_qr": f"TICKET-{next_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        result = tickets_collection.insert_one(ticket)
        ticket['_id'] = str(result.inserted_id)
        return ticket
    
    @staticmethod
    def update(ticket_id, data):
        data['updated_at'] = datetime.now().isoformat()
        
        result = tickets_collection.update_one(
            {"id": ticket_id},
            {"$set": data}
        )
        
        if result.modified_count > 0:
            return Ticket.find_by_id(ticket_id)
        return None
    
    @staticmethod
    def delete(ticket_id):
        result = tickets_collection.delete_one({"id": ticket_id})
        return result.deleted_count > 0


@tickets_bp.route('/', methods=['GET'])
@jwt_required
def get_tickets():
    """Obtener todos los tickets"""
    try:
        estado = request.args.get('estado', None)
        usuario_id = request.args.get('usuario_id', None)
        pelicula_id = request.args.get('pelicula_id', None)
        sala_id = request.args.get('sala_id', None)
        fecha = request.args.get('fecha', None)
        
        tickets = Ticket.get_all()
        
        # Filtros
        if estado:
            tickets = [t for t in tickets if t['estado'].lower() == estado.lower()]
        
        if usuario_id:
            tickets = [t for t in tickets if t['usuario_id'] == int(usuario_id)]
        
        if pelicula_id:
            tickets = [t for t in tickets if t['pelicula_id'] == int(pelicula_id)]
        
        if sala_id:
            tickets = [t for t in tickets if t['sala_id'] == int(sala_id)]
        
        if fecha:
            tickets = [t for t in tickets if t['fecha_funcion'] == fecha]
        
        # Si no es admin/cajero, solo ver sus propios tickets
        user_role = request.current_user.get('role')
        if user_role not in ['admin', 'cajero']:
            user_id = request.current_user.get('user_id')
            tickets = [t for t in tickets if t['usuario_id'] == user_id]
        
        return jsonify({
            'success': True,
            'message': 'Tickets obtenidos exitosamente',
            'data': tickets,
            'count': len(tickets)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al obtener tickets: {str(e)}'
        }), 500


@tickets_bp.route('/<int:ticket_id>', methods=['GET'])
@jwt_required
def get_ticket(ticket_id):
    """Obtener un ticket por ID"""
    try:
        ticket = Ticket.find_by_id(ticket_id)
        
        if not ticket:
            return jsonify({
                'success': False,
                'message': 'Ticket no encontrado'
            }), 404
        
        # Verificar permisos: admin/cajero puede ver todos, cliente solo los suyos
        user_role = request.current_user.get('role')
        user_id = request.current_user.get('user_id')
        
        if user_role not in ['admin', 'cajero'] and ticket['usuario_id'] != user_id:
            return jsonify({
                'success': False,
                'message': 'No tienes permiso para ver este ticket'
            }), 403
        
        return jsonify({
            'success': True,
            'message': 'Ticket obtenido exitosamente',
            'data': ticket
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al obtener ticket: {str(e)}'
        }), 500


# tickets.py - REEMPLAZAR LA FUNCIÓN create_ticket COMPLETA

@tickets_bp.route('/', methods=['POST'])
@jwt_required
def create_ticket():
    """Crear un nuevo ticket - VERSIÓN CORREGIDA"""
    try:
        data = request.get_json()
        
        required_fields = ['pelicula_id', 'sala_id', 'asiento', 'fecha_funcion', 'hora_funcion', 'precio']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'El campo {field} es requerido'
                }), 400
        
        # ✅ CONVERTIR A INT
        try:
            pelicula_id = int(data['pelicula_id'])
            sala_id = int(data['sala_id'])
        except (ValueError, TypeError):
            return jsonify({
                'success': False,
                'message': 'IDs de película y sala deben ser números válidos'
            }), 400
        
        # Validar película existe
        pelicula = peliculas_collection.find_one({"id": pelicula_id})
        if not pelicula:
            return jsonify({
                'success': False,
                'message': f'La película con ID {pelicula_id} no existe'
            }), 404
        
        # Validar sala existe
        sala = salas_collection.find_one({"id": sala_id})
        if not sala:
            return jsonify({
                'success': False,
                'message': f'La sala con ID {sala_id} no existe'
            }), 404
        
        # Validar usuario (usar el del token si no se especifica)
        usuario_id = data.get('usuario_id', request.current_user.get('user_id'))
        usuario = usuarios_collection.find_one({"id": usuario_id})
        if not usuario:
            return jsonify({
                'success': False,
                'message': 'El usuario no existe'
            }), 404
        
        # Verificar que el asiento no esté ocupado para esa función
        asiento_ocupado = tickets_collection.find_one({
            "sala_id": sala_id,
            "fecha_funcion": data['fecha_funcion'],
            "hora_funcion": data['hora_funcion'],
            "asiento": data['asiento'],
            "estado": {"$in": ["reservado", "pagado"]}
        })
        
        if asiento_ocupado:
            return jsonify({
                'success': False,
                'message': f'El asiento {data["asiento"]} ya está ocupado para esta función'
            }), 409
        
        # Validar precio
        try:
            precio = float(data['precio'])
            if precio <= 0:
                raise ValueError
        except (ValueError, TypeError):
            return jsonify({
                'success': False,
                'message': 'El precio debe ser un número válido mayor a 0'
            }), 400
        
        # ✅ PREPARAR DATOS DEL TICKET CON IDS COMO INT Y PRECIO COMO FLOAT
        ticket_data = {
            'pelicula_id': pelicula_id,  # ✅ INT
            'sala_id': sala_id,  # ✅ INT
            'pelicula_nombre': pelicula['titulo'],  # ✅ STRING
            'sala_nombre': sala['nombre'],  # ✅ STRING
            'usuario_id': usuario_id,
            'usuario_nombre': usuario['name'],
            'asiento': data['asiento'],
            'fecha_funcion': data['fecha_funcion'],
            'hora_funcion': data['hora_funcion'],
            'precio': precio,  # ✅ FLOAT
            'estado': data.get('estado', 'reservado'),
            'metodo_pago': data.get('metodo_pago', 'efectivo')
        }
        
        # ✅ LOG PARA DEBUG
        print(f"\n{'='*50}")
        print(f"🎟️ CREANDO TICKET:")
        print(f"   - Película: {ticket_data['pelicula_nombre']} (ID: {pelicula_id})")
        print(f"   - Sala: {ticket_data['sala_nombre']} (ID: {sala_id})")
        print(f"   - Precio: ${precio}")
        print(f"   - Asiento: {ticket_data['asiento']}")
        print(f"   - Fecha: {ticket_data['fecha_funcion']} {ticket_data['hora_funcion']}")
        print(f"{'='*50}\n")
        
        nuevo_ticket = Ticket.create(ticket_data)
        
        return jsonify({
            'success': True,
            'message': 'Ticket creado exitosamente',
            'data': nuevo_ticket
        }), 201
        
    except Exception as e:
        print(f"\n❌ Error al crear ticket: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Error al crear ticket: {str(e)}'
        }), 500

@tickets_bp.route('/<int:ticket_id>', methods=['PUT', 'PATCH'])
@admin_or_cajero_required
def update_ticket(ticket_id):
    """Actualizar un ticket"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No se enviaron datos para actualizar'
            }), 400
        
        ticket_existente = Ticket.find_by_id(ticket_id)
        if not ticket_existente:
            return jsonify({
                'success': False,
                'message': 'Ticket no encontrado'
            }), 404
        
        # Validar precio si se actualiza
        if 'precio' in data:
            try:
                precio = float(data['precio'])
                if precio <= 0:
                    raise ValueError
            except (ValueError, TypeError):
                return jsonify({
                    'success': False,
                    'message': 'El precio debe ser un número válido mayor a 0'
                }), 400
        
        ticket_actualizado = Ticket.update(ticket_id, data)
        
        if not ticket_actualizado:
            return jsonify({
                'success': False,
                'message': 'Error al actualizar ticket'
            }), 500
        
        return jsonify({
            'success': True,
            'message': 'Ticket actualizado exitosamente',
            'data': ticket_actualizado
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al actualizar ticket: {str(e)}'
        }), 500


@tickets_bp.route('/<int:ticket_id>', methods=['DELETE']) 
@admin_or_cajero_required
def delete_ticket(ticket_id):
    """Eliminar/Cancelar un ticket"""
    try:
        ticket = Ticket.find_by_id(ticket_id)
        if not ticket:
            return jsonify({
                'success': False,
                'message': 'Ticket no encontrado'
            }), 404
        
        # En lugar de eliminar, marcar como cancelado
        Ticket.update(ticket_id, {"estado": "cancelado"})
        
        return jsonify({
            'success': True,
            'message': 'Ticket cancelado exitosamente'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al cancelar ticket: {str(e)}'
        }), 500


@tickets_bp.route('/stats', methods=['GET'])
@admin_or_cajero_required
def get_tickets_stats():
    """Obtener estadísticas de tickets"""
    try:
        tickets = Ticket.get_all()
        
        total = len(tickets)
        
        estados = {}
        for t in tickets:
            estado = t['estado']
            estados[estado] = estados.get(estado, 0) + 1
        
        # Calcular ingresos totales
        ingresos = sum(t['precio'] for t in tickets if t['estado'] in ['pagado', 'reservado'])
        
        return jsonify({
            'success': True,
            'message': 'Estadísticas obtenidas exitosamente',
            'data': {
                'total': total,
                'por_estado': estados,
                'reservados': estados.get('reservado', 0),
                'pagados': estados.get('pagado', 0),
                'cancelados': estados.get('cancelado', 0),
                'ingresos_totales': round(ingresos, 2)
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al obtener estadísticas: {str(e)}'
        }), 500


@tickets_bp.route('/disponibilidad', methods=['GET'])
@jwt_required
def get_disponibilidad():
    """Obtener asientos disponibles para una función"""
    try:
        sala_id = request.args.get('sala_id')
        fecha = request.args.get('fecha')
        hora = request.args.get('hora')
        
        if not sala_id or not fecha or not hora:
            return jsonify({
                'success': False,
                'message': 'sala_id, fecha y hora son requeridos'
            }), 400
        
        # Obtener sala
        sala = salas_collection.find_one({"id": int(sala_id)})
        if not sala:
            return jsonify({
                'success': False,
                'message': 'Sala no encontrada'
            }), 404
        
        # Obtener tickets ocupados
        tickets_ocupados = list(tickets_collection.find({
            "sala_id": int(sala_id),
            "fecha_funcion": fecha,
            "hora_funcion": hora,
            "estado": {"$in": ["reservado", "pagado"]}
        }))
        
        asientos_ocupados = [t['asiento'] for t in tickets_ocupados]
        
        # Generar matriz de asientos
        filas = sala['filas']
        asientos_por_fila = sala['asientos_por_fila']
        
        asientos = []
        for fila in range(1, filas + 1):
            for numero in range(1, asientos_por_fila + 1):
                asiento_nombre = f"{chr(64 + fila)}{numero}"
                asientos.append({
                    "nombre": asiento_nombre,
                    "fila": fila,
                    "numero": numero,
                    "disponible": asiento_nombre not in asientos_ocupados
                })
        
        return jsonify({
            'success': True,
            'message': 'Disponibilidad obtenida exitosamente',
            'data': {
                'sala': {
                    'id': sala['id'],
                    'nombre': sala['nombre'],
                    'filas': filas,
                    'asientos_por_fila': asientos_por_fila,
                    'capacidad_total': sala['capacidad']
                },
                'asientos': asientos,
                'disponibles': len([a for a in asientos if a['disponible']]),
                'ocupados': len(asientos_ocupados)
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al obtener disponibilidad: {str(e)}'
        }), 500