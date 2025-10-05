import json
import jwt
from datetime import datetime, timedelta
from functools import wraps

# Configuración
JWT_SECRET = "tu_clave_secreta_super_segura_2024"
JWT_ALGORITHM = "HS256"

# Base de datos en memoria (considera usar DynamoDB en producción)
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

def get_token_from_headers(headers):
    """Extrae el token del header Authorization"""
    if not headers:
        return None
    
    auth_header = headers.get('Authorization') or headers.get('authorization')
    if not auth_header:
        return None
    
    try:
        return auth_header.split(" ")[1]
    except IndexError:
        return None

def create_response(status_code, body):
    """Crea una respuesta HTTP formateada para API Gateway"""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,Authorization',
            'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
        },
        'body': json.dumps(body, ensure_ascii=False)
    }

def handle_home():
    """GET / - Endpoint raíz"""
    return create_response(200, {
        "message": "CineMax API funcionando en AWS Lambda",
        "status": "ok"
    })

def handle_register(body):
    """POST /api/auth/register - Registro de usuarios"""
    try:
        if not body:
            return create_response(400, {
                "success": False,
                "message": "No se enviaron datos"
            })
        
        email = body.get('email')
        password = body.get('password')
        name = body.get('name')
        role = body.get('role', 'employee')
        
        if not email or not password or not name:
            return create_response(400, {
                "success": False,
                "message": "Email, password y nombre son requeridos"
            })
        
        # Verificar si el usuario ya existe
        existing_user = next((u for u in users if u['email'] == email), None)
        if existing_user:
            return create_response(409, {
                "success": False,
                "message": "El usuario ya existe"
            })
        
        # Crear nuevo usuario
        new_user = {
            "id": len(users) + 1,
            "email": email,
            "password": password,
            "name": name,
            "role": role,
            "permissions": ["all"] if role == "admin" else ["read"]
        }
        
        users.append(new_user)
        
        return create_response(200, {
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
        return create_response(500, {
            "success": False,
            "message": "Error interno del servidor"
        })

def handle_login(body):
    """POST /api/auth/login - Inicio de sesión"""
    try:
        if not body:
            return create_response(400, {
                "success": False,
                "message": "No se enviaron datos"
            })
        
        email = body.get('email')
        password = body.get('password')
        
        if not email or not password:
            return create_response(400, {
                "success": False,
                "message": "Email y password son requeridos"
            })
        
        # Buscar usuario
        user = next((u for u in users if u['email'] == email), None)
        
        if not user:
            return create_response(401, {
                "success": False,
                "message": "Usuario no encontrado"
            })
        
        # Verificar contraseña
        if user['password'] != password:
            return create_response(401, {
                "success": False,
                "message": "Contraseña incorrecta"
            })
        
        # Generar token
        access_token = generate_jwt_token(user)
        
        return create_response(200, {
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
        return create_response(500, {
            "success": False,
            "message": "Error interno del servidor"
        })

def handle_verify_token(headers):
    """GET /api/auth/verify - Verificar token"""
    token = get_token_from_headers(headers)
    
    if not token:
        return create_response(401, {
            "success": False,
            "message": "Token faltante"
        })
    
    payload = verify_jwt_token(token)
    if payload is None:
        return create_response(401, {
            "success": False,
            "message": "Token inválido o expirado"
        })
    
    return create_response(200, {
        "success": True,
        "message": "Token válido",
        "data": {
            "user": payload
        }
    })

def handle_get_profile(headers):
    """GET /api/profile - Obtener perfil del usuario"""
    token = get_token_from_headers(headers)
    
    if not token:
        return create_response(401, {
            "success": False,
            "message": "Token faltante"
        })
    
    user_data = verify_jwt_token(token)
    if user_data is None:
        return create_response(401, {
            "success": False,
            "message": "Token inválido o expirado"
        })
    
    return create_response(200, {
        "success": True,
        "message": "Perfil obtenido exitosamente",
        "data": {
            "user_id": user_data['user_id'],
            "email": user_data['email'],
            "role": user_data['role'],
            "permissions": user_data['permissions']
        }
    })

def handle_get_users():
    """GET /api/users - Listar usuarios (solo para debug)"""
    return create_response(200, {
        "users": [{"email": u["email"], "role": u["role"]} for u in users]
    })

def handle_admin_only(headers):
    """GET /api/admin-only - Endpoint solo para administradores"""
    token = get_token_from_headers(headers)
    
    if not token:
        return create_response(401, {
            "success": False,
            "message": "Token faltante"
        })
    
    user_data = verify_jwt_token(token)
    if user_data is None:
        return create_response(401, {
            "success": False,
            "message": "Token inválido o expirado"
        })
    
    if 'admin' not in user_data['role']:
        return create_response(403, {
            "success": False,
            "message": "Acceso denegado. Solo administradores."
        })
    
    return create_response(200, {
        "success": True,
        "message": "Acceso de administrador concedido",
        "data": {
            "message": "¡Hola Administrador!",
            "timestamp": datetime.utcnow().isoformat()
        }
    })

def lambda_handler(event, context):
    """
    Manejador principal de AWS Lambda
    """
    print(f"Event: {json.dumps(event)}")
    
    # Manejar preflight CORS
    if event.get('httpMethod') == 'OPTIONS':
        return create_response(200, {"message": "OK"})
    
    # Obtener método HTTP y ruta
    http_method = event.get('httpMethod', '')
    path = event.get('path', '')
    headers = event.get('headers', {})
    
    # Parsear body si existe
    body = None
    if event.get('body'):
        try:
            body = json.loads(event['body'])
        except:
            body = {}
    
    # Enrutamiento
    try:
        # Ruta raíz
        if path == '/' and http_method == 'GET':
            return handle_home()
        
        # Autenticación
        elif path == '/api/auth/register' and http_method == 'POST':
            return handle_register(body)
        
        elif path == '/api/auth/login' and http_method == 'POST':
            return handle_login(body)
        
        elif path == '/api/auth/verify' and http_method == 'GET':
            return handle_verify_token(headers)
        
        # Perfil
        elif path == '/api/profile' and http_method == 'GET':
            return handle_get_profile(headers)
        
        # Usuarios
        elif path == '/api/users' and http_method == 'GET':
            return handle_get_users()
        
        # Admin
        elif path == '/api/admin-only' and http_method == 'GET':
            return handle_admin_only(headers)
        
        # Ruta no encontrada
        else:
            return create_response(404, {
                "success": False,
                "message": f"Ruta no encontrada: {http_method} {path}"
            })
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return create_response(500, {
            "success": False,
            "message": "Error interno del servidor",
            "error": str(e)
        })