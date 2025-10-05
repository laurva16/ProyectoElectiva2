# server.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import jwt
from datetime import datetime, timedelta
from functools import wraps

from config import JWT_SECRET, JWT_ALGORITHM, PORT, DEBUG
from models import Usuario, Pelicula
from peliculas import peliculas_bp

app = Flask(__name__)
CORS(app, origins=["http://localhost:4200"], supports_credentials=True)

app.register_blueprint(peliculas_bp)


def generate_jwt_token(user):
    payload = {
        'user_id': user['id'],
        'email': user['email'],
        'role': user['role'],
        'permissions': user['permissions'],
        'exp': datetime.utcnow() + timedelta(hours=24),
        'iat': datetime.utcnow(),
        'iss': 'cinemax-api'
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def verify_jwt_token(token):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except:
        return None


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
        
        payload = verify_jwt_token(token)
        if payload is None:
            return jsonify({'success': False, 'message': 'Token inválido o expirado'}), 401
        
        request.current_user = payload
        return f(*args, **kwargs)
    
    return decorated


@app.route('/')
def home():
    return jsonify({
        "message": "CineMax API funcionando con MongoDB Atlas",
        "status": "ok",
        "version": "3.0",
        "database": "MongoDB Atlas"
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
        
        if Usuario.find_by_email(email):
            return jsonify({
                "success": False,
                "message": "El usuario ya existe"
            }), 409
        
        new_user = Usuario.create(email, password, name, role)
        
        if not new_user:
            return jsonify({
                "success": False,
                "message": "Error al crear usuario"
            }), 500
        
        user_response = {k: v for k, v in new_user.items() if k not in ['password', '_id']}
        
        return jsonify({
            "success": True,
            "message": "Usuario registrado exitosamente",
            "data": {"user": user_response}
        }), 201
        
    except Exception as e:
        print(f"Error en registro: {str(e)}")
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
        
        user = Usuario.find_by_email(email)
        
        if not user:
            return jsonify({
                "success": False,
                "message": "Usuario no encontrado"
            }), 401
        
        if user['password'] != password:
            return jsonify({
                "success": False,
                "message": "Contraseña incorrecta"
            }), 401
        
        access_token = generate_jwt_token(user)
        user_data = {k: v for k, v in user.items() if k not in ['password', '_id']}
        
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
        print(f"Error en login: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"Error interno del servidor: {str(e)}"
        }), 500


@app.route('/api/auth/verify', methods=['GET'])
@jwt_required
def verify_token():
    return jsonify({
        "success": True,
        "message": "Token válido",
        "data": {"user": request.current_user}
    })


@app.route('/api/profile', methods=['GET'])
@jwt_required
def get_profile():
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


if __name__ == '__main__':
    print("=" * 60)
    print("CineMax API v3.0 - MongoDB Atlas Edition")
    print("=" * 60)
    print(f"Servidor iniciado en http://localhost:{PORT}")
    print("CORS habilitado para http://localhost:4200")
    print("JWT Autenticación activa")
    print("Base de datos: MongoDB Atlas")
    print("Módulo de Películas cargado")
    print("=" * 60)
    app.run(port=PORT, debug=DEBUG)