#!/usr/bin/env python3
# test_client.py - Cliente de prueba para la API

import requests
import json
from datetime import datetime

class CineMaxAPIClient:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.token = None
        self.session = requests.Session()
        
    def login(self, email, password, remember_me=False):
        """Iniciar sesión"""
        url = f"{self.base_url}/api/auth/login"
        data = {
            "email": email,
            "password": password,
            "rememberMe": remember_me
        }
        
        try:
            response = self.session.post(url, json=data)
            result = response.json()
            
            if result.get('success'):
                self.token = result['data']['access_token']
                self.session.headers.update({
                    'Authorization': f"Bearer {self.token}"
                })
                print(f"✅ Login exitoso: {result['message']}")
                print(f"👤 Usuario: {result['data']['user']['name']}")
                print(f"🎭 Rol: {result['data']['user']['role']}")
                return result
            else:
                print(f"❌ Error en login: {result['message']}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Error de conexión: {e}")
            return None
    
    def get_profile(self):
        """Obtener perfil de usuario"""
        if not self.token:
            print("❌ No hay sesión activa")
            return None
            
        url = f"{self.base_url}/api/auth/profile"
        
        try:
            response = self.session.get(url)
            result = response.json()
            
            if result.get('success'):
                print("✅ Perfil obtenido:")
                print(f"📧 Email: {result['data']['email']}")
                print(f"👤 Nombre: {result['data']['name']}")
                print(f"🎭 Rol: {result['data']['role']}")
                print(f"🔑 Permisos: {', '.join(result['data']['permissions'])}")
                return result
            else:
                print(f"❌ Error obteniendo perfil: {result['message']}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Error de conexión: {e}")
            return None
    
    def get_dashboard(self):
        """Acceder al dashboard"""
        if not self.token:
            print("❌ No hay sesión activa")
            return None
            
        url = f"{self.base_url}/api/dashboard"
        
        try:
            response = self.session.get(url)
            result = response.json()
            
            if result.get('success'):
                print("✅ Dashboard cargado:")
                data = result['data']
                print(f"👋 {data['welcome_message']}")
                print(f"⏰ Último login: {data['last_login']}")
                
                if 'admin_stats' in data:
                    stats = data['admin_stats']
                    print("📊 Estadísticas de admin:")
                    print(f"   👥 Total usuarios: {stats['total_users']}")
                    print(f"   🔒 Sesiones cerradas: {stats['active_sessions']}")
                    print(f"   ⚡ Estado del sistema: {stats['system_status']}")
                
                return result
            else:
                print(f"❌ Error cargando dashboard: {result['message']}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Error de conexión: {e}")
            return None
    
    def verify_token(self):
        """Verificar token actual"""
        if not self.token:
            print("❌ No hay token para verificar")
            return None
            
        url = f"{self.base_url}/api/auth/verify"
        
        try:
            response = self.session.post(url)
            result = response.json()
            
            if result.get('success'):
                print("✅ Token válido")
                data = result['data']
                print(f"👤 ID Usuario: {data['user_id']}")
                print(f"🎭 Rol: {data['role']}")
                print(f"🔑 Permisos: {', '.join(data['permissions'])}")
                return result
            else:
                print(f"❌ Token inválido: {result['message']}")
                self.token = None
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Error de conexión: {e}")
            return None
    
    def logout(self):
        """Cerrar sesión"""
        if not self.token:
            print("❌ No hay sesión activa")
            return None
            
        url = f"{self.base_url}/api/auth/logout"
        
        try:
            response = self.session.post(url)
            result = response.json()
            
            if result.get('success'):
                print(f"✅ {result['message']}")
                self.token = None
                self.session.headers.pop('Authorization', None)
                return result
            else:
                print(f"❌ Error cerrando sesión: {result['message']}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Error de conexión: {e}")
            return None

def test_api():
    """Función de prueba completa"""
    print("🎬 Iniciando pruebas de CineMax API")
    print("=" * 50)
    
    client = CineMaxAPIClient()
    
    # Probar servidor
    try:
        response = requests.get("http://localhost:5000")
        if response.status_code == 200:
            print("🚀 Servidor funcionando correctamente")
        else:
            print("❌ Servidor no responde correctamente")
            return
    except:
        print("❌ No se puede conectar al servidor. ¿Está corriendo?")
        return
    
    print("\n" + "="*30)
    print("1️⃣ PROBANDO LOGIN ADMINISTRADOR")
    print("="*30)
    
    # Login como admin
    login_result = client.login("admin@cinemax.com", "admin123", remember_me=True)
    
    if login_result:
        print("\n🔍 Verificando token...")
        client.verify_token()
        
        print("\n👤 Obteniendo perfil...")
        client.get_profile()
        
        print("\n📊 Cargando dashboard...")
        client.get_dashboard()
        
        print("\n🚪 Cerrando sesión...")
        client.logout()
    
    print("\n" + "="*30)
    print("2️⃣ PROBANDO LOGIN EMPLEADO")
    print("="*30)
    
    # Login como empleado
    client2 = CineMaxAPIClient()
    login_result = client2.login("empleado@cinemax.com", "emp123")
    
    if login_result:
        print("\n📊 Cargando dashboard de empleado...")
        client2.get_dashboard()
        
        print("\n🚪 Cerrando sesión...")
        client2.logout()
    
    print("\n" + "="*30)
    print("3️⃣ PROBANDO CREDENCIALES INCORRECTAS")
    print("="*30)
    
    # Probar credenciales incorrectas
    client3 = CineMaxAPIClient()
    client3.login("usuario@inexistente.com", "password123")
    
    print("\n" + "="*30)
    print("4️⃣ PROBANDO ACCESO SIN TOKEN")
    print("="*30)
    
    # Probar acceso sin token
    client4 = CineMaxAPIClient()
    client4.get_profile()
    client4.get_dashboard()
    
    print("\n🎉 Pruebas completadas!")

if __name__ == "__main__":
    test_api()