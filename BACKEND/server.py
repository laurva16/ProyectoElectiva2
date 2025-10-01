from flask import Flask, request, jsonify
from flask_cors import CORS
import jwt
from datetime import datetime, timedelta
from functools import wraps
from boleta_service import BoletaService, Boleta

app = Flask(__name__)
CORS(app, origins=["http://localhost:4200"], supports_credentials=True)

# Clave secreta para firmar los JWT (en producción usa una más segura)
JWT_SECRET = "tu_clave_secreta_super_segura_2024"
JWT_ALGORITHM = "HS256"

# Crear instancia del servicio de boletas
boleta_service = BoletaService()

users = [
    {
        "id": 1,
        "email": "admin@cinemax.com",
        "password": "admin123",
        "name": "Administrador",
        "role": "admin",
        "permissions": ["all"]
    },
    {
        "id": 2,
        "email": "empleado@cinemax.com",
        "password": "emp123",
        "name": "Empleado",
        "role": "employee",
        "permissions": ["read"]
    }
]

def generate_jwt_token(user):
    """Genera un token JWT para el usuario"""
    payload = {
        'user_id': user['id'],
        'email': user['email'],
        'role': user['role'],
        'permissions': user['permissions'],
        'exp': datetime.utcnow() + timedelta(hours=24),
        'iat': datetime.utcnow(),
        'iss': 'cinemax-api'
    }
    
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token

def verify_jwt_token(token):
    """Verifica y decodifica un token JWT"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

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
        
        payload = verify_jwt_token(token)
        if payload is None:
            return jsonify({'success': False, 'message': 'Token inválido o expirado'}), 401
        
        request.current_user = payload
        return f(*args, **kwargs)
    
    return decorated

# ============== RUTAS GENERALES ==============

@app.route('/')
def home():
    return jsonify({"message": "CineMax API funcionando", "status": "ok"})

# ============== RUTAS DE AUTENTICACIÓN ==============

@app.route('/api/auth/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"success": False, "message": "No se enviaron datos"}), 400
        
        email = data.get('email')
        password = data.get('password')
        name = data.get('name')
        role = data.get('role', 'employee')
        
        if not email or not password or not name:
            return jsonify({"success": False, "message": "Email, password y nombre son requeridos"}), 400
        
        existing_user = next((u for u in users if u['email'] == email), None)
        if existing_user:
            return jsonify({"success": False, "message": "El usuario ya existe"}), 409
        
        new_user = {
            "id": len(users) + 1,
            "email": email,
            "password": password,
            "name": name,
            "role": role,
            "permissions": ["all"] if role == "admin" else ["read"]
        }
        
        users.append(new_user)
        
        return jsonify({
            "success": True,
            "message": "Usuario registrado exitosamente",
            "data": {
                "user": {
                    "id": new_user["id"],
                    "name": new_user["name"],
                    "email": new_user["email"],
                    "role": new_user["role"],
                    "permissions": new_user["permissions"]
                }
            }
        })
        
    except Exception as e:
        return jsonify({"success": False, "message": "Error interno del servidor"}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"success": False, "message": "No se enviaron datos"}), 400
        
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({"success": False, "message": "Email y password son requeridos"}), 400
        
        user = next((u for u in users if u['email'] == email), None)
        
        if not user:
            return jsonify({"success": False, "message": "Usuario no encontrado"}), 401
        
        if user['password'] != password:
            return jsonify({"success": False, "message": "Contraseña incorrecta"}), 401
        
        access_token = generate_jwt_token(user)
        
        return jsonify({
            "success": True,
            "message": "Login exitoso",
            "data": {
                "user": {
                    "id": user["id"],
                    "name": user["name"],
                    "email": user["email"],
                    "role": user["role"],
                    "permissions": user["permissions"]
                },
                "access_token": access_token,
                "token_type": "Bearer",
                "expires_in": 86400
            }
        })
        
    except Exception as e:
        return jsonify({"success": False, "message": "Error interno del servidor"}), 500

@app.route('/api/auth/verify', methods=['GET'])
@jwt_required
def verify_token():
    """Endpoint para verificar si el token es válido"""
    return jsonify({
        "success": True,
        "message": "Token válido",
        "data": {
            "user": request.current_user
        }
    })

@app.route('/api/profile', methods=['GET'])
@jwt_required
def get_profile():
    """Endpoint protegido que requiere autenticación"""
    user_data = request.current_user
    return jsonify({
        "success": True,
        "message": "Perfil obtenido exitosamente",
        "data": {
            "user_id": user_data['user_id'],
            "email": user_data['email'],
            "role": user_data['role'],
            "permissions": user_data['permissions']
        }
    })

@app.route('/api/users', methods=['GET'])
def get_users():
    return jsonify({
        "users": [{"email": u["email"], "role": u["role"]} for u in users]
    })

@app.route('/api/admin-only', methods=['GET'])
@jwt_required
def admin_only():
    """Endpoint solo para administradores"""
    user_data = request.current_user
    
    if 'admin' not in user_data['role']:
        return jsonify({
            "success": False,
            "message": "Acceso denegado. Solo administradores."
        }), 403
    
    return jsonify({
        "success": True,
        "message": "Acceso de administrador concedido",
        "data": {
            "message": "¡Hola Administrador!",
            "timestamp": datetime.utcnow().isoformat()
        }
    })

# ============== ENDPOINTS DE BOLETAS ==============

@app.route('/api/boletas', methods=['GET'])
@jwt_required
def listar_boletas():
    """Lista todas las boletas con filtros opcionales"""
    try:
        tipo_boleta = request.args.get('tipo_boleta')
        sala = request.args.get('sala')
        pelicula = request.args.get('pelicula')
        
        boletas = boleta_service.listar_boletas(
            tipo_boleta=tipo_boleta,
            sala=sala,
            pelicula=pelicula
        )
        
        return jsonify({
            "success": True,
            "message": "Boletas obtenidas exitosamente",
            "data": {
                "boletas": [boleta.to_dict() for boleta in boletas],
                "total": len(boletas)
            }
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error al listar boletas: {str(e)}"
        }), 500

@app.route('/api/boletas/<string:id_boleta>', methods=['GET'])
@jwt_required
def obtener_boleta(id_boleta):
    """Obtiene una boleta específica por ID"""
    try:
        boleta = boleta_service.obtener_boleta(id_boleta)
        
        if not boleta:
            return jsonify({
                "success": False,
                "message": "Boleta no encontrada"
            }), 404
        
        return jsonify({
            "success": True,
            "message": "Boleta obtenida exitosamente",
            "data": {
                "boleta": boleta.to_dict()
            }
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error al obtener boleta: {str(e)}"
        }), 500

@app.route('/api/boletas', methods=['POST'])
@jwt_required
def crear_boleta():
    """Crea una nueva boleta (solo admin)"""
    try:
        user_data = request.current_user
        
        if user_data['role'] != 'admin':
            return jsonify({
                "success": False,
                "message": "Acceso denegado. Solo administradores pueden crear boletas."
            }), 403
        
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "message": "No se enviaron datos"
            }), 400
        
        required_fields = ['tipo_boleta', 'sala', 'fecha_hora', 'pelicula']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    "success": False,
                    "message": f"Campo requerido faltante: {field}"
                }), 400
        
        fecha_hora = datetime.fromisoformat(data['fecha_hora'].replace('Z', '+00:00'))
        
        boleta = boleta_service.crear_boleta(
            tipo_boleta=data['tipo_boleta'],
            sala=data['sala'],
            fecha_hora=fecha_hora,
            pelicula=data['pelicula'],
            precio=data.get('precio')
        )
        
        return jsonify({
            "success": True,
            "message": "Boleta creada exitosamente",
            "data": {
                "boleta": boleta.to_dict()
            }
        }), 201
        
    except ValueError as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 400
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error al crear boleta: {str(e)}"
        }), 500

@app.route('/api/boletas/<string:id_boleta>', methods=['PUT'])
@jwt_required
def actualizar_boleta(id_boleta):
    """Actualiza una boleta existente (solo admin)"""
    try:
        user_data = request.current_user
        
        if user_data['role'] != 'admin':
            return jsonify({
                "success": False,
                "message": "Acceso denegado. Solo administradores pueden actualizar boletas."
            }), 403
        
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "message": "No se enviaron datos"
            }), 400
        
        fecha_hora = None
        if 'fecha_hora' in data:
            fecha_hora = datetime.fromisoformat(data['fecha_hora'].replace('Z', '+00:00'))
        
        boleta = boleta_service.actualizar_boleta(
            id_boleta=id_boleta,
            tipo_boleta=data.get('tipo_boleta'),
            sala=data.get('sala'),
            fecha_hora=fecha_hora,
            pelicula=data.get('pelicula'),
            precio=data.get('precio')
        )
        
        if not boleta:
            return jsonify({
                "success": False,
                "message": "Boleta no encontrada"
            }), 404
        
        return jsonify({
            "success": True,
            "message": "Boleta actualizada exitosamente",
            "data": {
                "boleta": boleta.to_dict()
            }
        })
        
    except ValueError as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 400
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error al actualizar boleta: {str(e)}"
        }), 500

@app.route('/api/boletas/<string:id_boleta>', methods=['DELETE'])
@jwt_required
def eliminar_boleta(id_boleta):
    """Elimina una boleta (solo admin)"""
    try:
        user_data = request.current_user
        
        if user_data['role'] != 'admin':
            return jsonify({
                "success": False,
                "message": "Acceso denegado. Solo administradores pueden eliminar boletas."
            }), 403
        
        eliminada = boleta_service.eliminar_boleta(id_boleta)
        
        if not eliminada:
            return jsonify({
                "success": False,
                "message": "Boleta no encontrada"
            }), 404
        
        return jsonify({
            "success": True,
            "message": "Boleta eliminada exitosamente"
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error al eliminar boleta: {str(e)}"
        }), 500

@app.route('/api/boletas/estadisticas', methods=['GET'])
@jwt_required
def obtener_estadisticas():
    """Obtiene estadísticas de las boletas (solo admin)"""
    try:
        user_data = request.current_user
        
        if user_data['role'] != 'admin':
            return jsonify({
                "success": False,
                "message": "Acceso denegado. Solo administradores pueden ver estadísticas."
            }), 403
        
        estadisticas = boleta_service.obtener_estadisticas()
        
        return jsonify({
            "success": True,
            "message": "Estadísticas obtenidas exitosamente",
            "data": estadisticas
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error al obtener estadísticas: {str(e)}"
        }), 500

@app.route('/api/boletas/fecha/<string:fecha>', methods=['GET'])
@jwt_required
def obtener_boletas_por_fecha(fecha):
    """Obtiene boletas por fecha (formato: YYYY-MM-DD)"""
    try:
        fecha_obj = datetime.strptime(fecha, '%Y-%m-%d')
        boletas = boleta_service.obtener_boletas_por_fecha(fecha_obj)
        
        return jsonify({
            "success": True,
            "message": f"Boletas para la fecha {fecha} obtenidas exitosamente",
            "data": {
                "boletas": [boleta.to_dict() for boleta in boletas],
                "total": len(boletas),
                "fecha": fecha
            }
        })
        
    except ValueError:
        return jsonify({
            "success": False,
            "message": "Formato de fecha inválido. Use YYYY-MM-DD"
        }), 400
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error al obtener boletas por fecha: {str(e)}"
        }), 500

# ============== MAIN ==============

if __name__ == '__main__':
    print("🎬 Iniciando CineMax API...")
    print("📍 Servidor corriendo en: http://localhost:5000")
    print("🔐 Usuario admin: admin@cinemax.com / admin123")
    print("👤 Usuario empleado: empleado@cinemax.com / emp123")
    app.run(port=5000, debug=True)