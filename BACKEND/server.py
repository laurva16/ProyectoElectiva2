from flask import Flask, request, jsonify
from flask_cors import CORS
import jwt
from datetime import datetime, timedelta
from functools import wraps

app = Flask(__name__)
CORS(app, origins=["http://localhost:4200"], supports_credentials=True)

# Clave secreta para firmar los JWT (en producción usa una más segura)
JWT_SECRET = "tu_clave_secreta_super_segura_2024"
JWT_ALGORITHM = "HS256"

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
        'exp': datetime.utcnow() + timedelta(hours=24),  # Expira en 24 horas
        'iat': datetime.utcnow(),  # Tiempo de emisión
        'iss': 'cinemax-api'  # Emisor
    }
    
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token

def verify_jwt_token(token):
    """Verifica y decodifica un token JWT"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None  # Token expirado
    except jwt.InvalidTokenError:
        return None  # Token inválido

def jwt_required(f):
    """Decorador para rutas que requieren autenticación JWT"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Buscar el token en el header Authorization
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]  # Bearer <token>
            except IndexError:
                return jsonify({'success': False, 'message': 'Token mal formateado'}), 401
        
        if not token:
            return jsonify({'success': False, 'message': 'Token faltante'}), 401
        
        # Verificar el token
        payload = verify_jwt_token(token)
        if payload is None:
            return jsonify({'success': False, 'message': 'Token inválido o expirado'}), 401
        
        # Pasar los datos del usuario a la función
        request.current_user = payload
        return f(*args, **kwargs)
    
    return decorated

@app.route('/')
def home():
    return jsonify({"message": "CineMax API funcionando", "status": "ok"})

@app.route('/api/auth/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"success": False, "message": "No se enviaron datos"}), 400
        
        email = data.get('email')
        password = data.get('password')
        name = data.get('name')
        role = data.get('role', 'employee')  # Por defecto empleado
        
        if not email or not password or not name:
            return jsonify({"success": False, "message": "Email, password y nombre son requeridos"}), 400
        
        # Verificar si el usuario ya existe
        existing_user = next((u for u in users if u['email'] == email), None)
        if existing_user:
            return jsonify({"success": False, "message": "El usuario ya existe"}), 409
        
        # Crear nuevo usuario
        new_user = {
            "id": len(users) + 1,
            "email": email,
            "password": password,  # En producción usar hash
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
        
        # Buscar usuario por email primero
        user = next((u for u in users if u['email'] == email), None)
        
        if not user:
            return jsonify({"success": False, "message": "Usuario no encontrado"}), 401
        
        # Verificar contraseña
        if user['password'] != password:
            return jsonify({"success": False, "message": "Contraseña incorrecta"}), 401
        
        # Si llegamos aquí, login exitoso
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
    # Solo para debug - quitar en producción
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

if __name__ == '__main__':
    app.run(port=5000, debug=True)