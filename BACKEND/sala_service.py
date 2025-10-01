#!/usr/bin/env python3
# salas_client.py - Cliente para gestión de salas en la API CineMax

import requests
from test_client import CineMaxAPIClient


class SalaService(CineMaxAPIClient):
    """Servicios para la gestión de salas"""

    def listar_salas(self):
        """Obtener todas las salas"""
        if not self.token:
            print("❌ No hay sesión activa")
            return None

        url = f"{self.base_url}/api/salas"
        try:
            response = self.session.get(url)
            result = response.json()
            if result.get('success'):
                print("✅ Salas obtenidas correctamente")
                for sala in result['data']:
                    print(f"🏟 ID: {sala['_id']} | Nombre: {sala['nombre']} | Capacidad: {sala['capacidad']}")
                return result
            else:
                print(f"❌ Error listando salas: {result['message']}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"❌ Error de conexión: {e}")
            return None

    def crear_sala(self, nombre, capacidad):
        """Crear una nueva sala"""
        if not self.token:
            print("❌ No hay sesión activa")
            return None

        url = f"{self.base_url}/api/salas"
        data = {
            "nombre": nombre,
            "capacidad": capacidad
        }

        try:
            response = self.session.post(url, json=data)
            result = response.json()
            if result.get('success'):
                print(f"✅ Sala creada: {result['data']['nombre']} con capacidad {result['data']['capacidad']}")
                return result
            else:
                print(f"❌ Error creando sala: {result['message']}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"❌ Error de conexión: {e}")
            return None

    def actualizar_sala(self, sala_id, nombre=None, capacidad=None):
        """Actualizar una sala existente"""
        if not self.token:
            print("❌ No hay sesión activa")
            return None

        url = f"{self.base_url}/api/salas/{sala_id}"
        data = {}
        if nombre:
            data["nombre"] = nombre
        if capacidad:
            data["capacidad"] = capacidad

        try:
            response = self.session.put(url, json=data)
            result = response.json()
            if result.get('success'):
                print(f"✅ Sala actualizada: {result['data']['nombre']} (Capacidad {result['data']['capacidad']})")
                return result
            else:
                print(f"❌ Error actualizando sala: {result['message']}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"❌ Error de conexión: {e}")
            return None

    def eliminar_sala(self, sala_id):
        """Eliminar una sala"""
        if not self.token:
            print("❌ No hay sesión activa")
            return None

        url = f"{self.base_url}/api/salas/{sala_id}"
        try:
            response = self.session.delete(url)
            result = response.json()
            if result.get('success'):
                print(f"✅ Sala eliminada: {result['message']}")
                return result
            else:
                print(f"❌ Error eliminando sala: {result['message']}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"❌ Error de conexión: {e}")
            return None


# === Pequeña prueba rápida si ejecutas directamente este archivo ===
if __name__ == "__main__":
    print("🎬 Pruebas de SalaService")
    client = SalaService()
    
    # Login con admin (ajusta según tus credenciales reales)
    client.login("admin@cinemax.com", "admin123")

    # Listar salas
    client.listar_salas()

    # Crear una sala de prueba
    nueva = client.crear_sala("Sala VIP", 50)

    if nueva:
        sala_id = nueva['data']['_id']

        # Actualizar sala
        client.actualizar_sala(sala_id, capacidad=80)

        # Eliminar sala
        client.eliminar_sala(sala_id)
