from flask import Flask, request, jsonify
from flask_cors import CORS
import jwt
from datetime import datetime, timedelta
from functools import wraps

# Importar el Blueprint de películas
from peliculas import peliculas_bp
from models import db

app = Flask(__name__)
CORS(app, origins=["http://localhost:4200"], supports_credentials=True)

# Clave secreta para firmar los JWT
JWT_SECRET = "tu_clave_secreta_super_segura_2024"
JWT_ALGORITHM = "HS256"

# Registrar el Blueprint de películas
app.register_blueprint(peliculas_bp)


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


@app.route('/')
def home():
    return jsonify({
        "message": "CineMax API funcionando",
        "status": "ok",
        "version": "2.0",
        "endpoints": {
            "auth": [
                "POST /api/auth/register",
                "POST /api/auth/login",
                "GET /api/auth/verify"
            ],
            "peliculas": [
                "GET /api/peliculas",
                "GET /api/peliculas/{id}",
                "POST /api/peliculas",
                "PUT /api/peliculas/{id}",
                "DELETE /api/peliculas/{id}",
                "GET /api/peliculas/stats"
            ]
        }
    })


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
            return jsonify({
                "success": False,
                "message": "Email, password y nombre son requeridos"
            }), 400
        
        # Verificar si el usuario ya existe
        existing_user = next((u for u in db.usuarios if u.email == email), None)
        if existing_user:
            return jsonify({
                "success": False,
                "message": "El usuario ya existe"
            }), 409
        
        # Crear nuevo usuario usando la clase Usuario
        from models import Usuario
        new_user = Usuario(
            id=len(db.usuarios) + 1,
            email=email,
            password=password,
            name=name,
            role=role
        )
        
        db.usuarios.append(new_user)
        
        return jsonify({
            "success": True,
            "message": "Usuario registrado exitosamente",
            "data": {
                "user": new_user.to_dict()
            }
        }), 201
        
    except Exception as e:
        print(f"Error en registro: {str(e)}")  # Debug
        return jsonify({
            "success": False,
            "message": f"Error interno del servidor: {str(e)}"
        }), 500


@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"success": False, "message": "No se enviaron datos"}), 400
        
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({
                "success": False,
                "message": "Email y password son requeridos"
            }), 400
        
        # Buscar usuario directamente en la lista de objetos Usuario
        user = next((u for u in db.usuarios if u.email == email), None)
        
        if not user:
            return jsonify({
                "success": False,
                "message": "Usuario no encontrado"
            }), 401
        
        # Verificar contraseña
        if user.password != password:
            return jsonify({
                "success": False,
                "message": "Contraseña incorrecta"
            }), 401
        
        # Convertir a dict sin password
        user_dict = user.to_dict(include_password=True)
        
        # Generar token
        access_token = generate_jwt_token(user_dict)
        
        # Remover password antes de enviar
        user_data = {k: v for k, v in user_dict.items() if k != 'password'}
        
        return jsonify({
            "success": True,
            "message": "Login exitoso",
            "data": {
                "user": user_data,
                "access_token": access_token,
                "token_type": "Bearer",
                "expires_in": 86400
            }
        })
        
    except Exception as e:
        print(f"Error en login: {str(e)}")  # Debug
        return jsonify({
            "success": False,
            "message": f"Error interno del servidor: {str(e)}"
        }), 500


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
    print("=" * 50)
    print("🎬 CineMax API v2.0")
    print("=" * 50)
    print("✅ Servidor iniciado en http://localhost:5000")
    print("📡 CORS habilitado para http://localhost:4200")
    print("🔐 JWT Autenticación activa")
    print("🎥 Módulo de Películas cargado")
    print("=" * 50)
    app.run(port=5000, debug=True)