import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule } from '@angular/router';
import { HttpClient, HttpHeaders } from '@angular/common/http';

interface Usuario {
  id?: number;
  name: string;
  email: string;
  role: string;
  telefono?: string;
  direccion?: string;
  created_at?: string;
  updated_at?: string;
}

@Component({
  selector: 'app-listar-usuarios',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './listar-usuarios.html',
  styleUrls: ['./listar-usuarios.css']  // ← Array con 's'
})
export class ListarUsuarios implements OnInit {
  usuarios: Usuario[] = [];
  usuariosFiltrados: Usuario[] = [];
  loading = false;
  searchTerm = '';
  filtroRol = '';
  roles: string[] = [];
  usuarioSeleccionado: Usuario | null = null;

  private apiUrl = 'http://localhost:5000/api/usuarios';

  constructor(
    private http: HttpClient,
    private router: Router
  ) {}

  ngOnInit() {
    this.cargarUsuarios();
  }

  cargarUsuarios() {
    this.loading = true;
    
    const token = localStorage.getItem('cinemax_token') || 
                  sessionStorage.getItem('cinemax_token');
    
    const headers = new HttpHeaders({
      'Authorization': `Bearer ${token}`
    });

    this.http.get<any>(this.apiUrl, { headers }).subscribe({
      next: (response) => {
        this.usuarios = response.data || [];
        this.usuariosFiltrados = [...this.usuarios];
        this.extraerRoles();
        this.loading = false;
        
        console.log('Usuarios cargados:', this.usuarios.length);
      },
      error: (error) => {
        console.error('Error al cargar usuarios:', error);
        this.loading = false;
        
        // Mostrar mensaje de error
        if (error.status === 403) {
          alert('No tienes permisos para ver los usuarios');
          this.router.navigate(['/dashboard']);
        } else {
          alert('Error al cargar usuarios: ' + (error.error?.message || 'Intenta nuevamente'));
        }
      }
    });
  }

  extraerRoles() {
    const rolesUnicos = new Set(this.usuarios.map(u => u.role));
    this.roles = Array.from(rolesUnicos);
  }

  buscar(event: Event) {
    const target = event.target as HTMLInputElement;
    this.searchTerm = target.value.toLowerCase();
    this.filtrarUsuarios();
  }

  filtrarPorRol(event: Event) {
    const target = event.target as HTMLSelectElement;
    this.filtroRol = target.value;
    this.filtrarUsuarios();
  }

  filtrarUsuarios() {
    this.usuariosFiltrados = this.usuarios.filter(usuario => {
      const coincideBusqueda = this.searchTerm === '' || 
        usuario.name.toLowerCase().includes(this.searchTerm) ||
        usuario.email.toLowerCase().includes(this.searchTerm);
      
      const coincideRol = this.filtroRol === '' || 
        usuario.role === this.filtroRol;
      
      return coincideBusqueda && coincideRol;
    });
  }

  getRolBadgeClass(role: string): string {
    switch (role) {
      case 'admin':
        return 'badge-admin';
      case 'cajero':
        return 'badge-cajero';
      case 'cliente':
        return 'badge-cliente';
      default:
        return 'badge-default';
    }
  }

  getRolLabel(role: string): string {
    switch (role) {
      case 'admin':
        return 'Administrador';
      case 'cajero':
        return 'Cajero';
      case 'cliente':
        return 'Cliente';
      default:
        return role;
    }
  }

  getRolIcon(role: string): string {
    switch (role) {
      case 'admin':
        return 'fas fa-user-shield';
      case 'cajero':
        return 'fas fa-cash-register';
      case 'cliente':
        return 'fas fa-user';
      default:
        return 'fas fa-user';
    }
  }

  verDetalle(usuario: Usuario, event?: Event) {
    if (event) {
      event.stopPropagation();
    }
    this.usuarioSeleccionado = usuario;
    document.body.style.overflow = 'hidden';
  }

  cerrarDetalle() {
    this.usuarioSeleccionado = null;
    document.body.style.overflow = 'auto';
  }

  editarUsuario(id: number, event?: Event) {
    if (event) {
      event.stopPropagation();
    }
    this.router.navigate(['/usuarios/editar', id]);
  }

  eliminarUsuario(id: number, event?: Event) {
    if (event) {
      event.stopPropagation();
    }

    if (!confirm('¿Estás seguro de que deseas eliminar este usuario? Esta acción no se puede deshacer.')) {
      return;
    }

    const token = localStorage.getItem('cinemax_token') || 
                  sessionStorage.getItem('cinemax_token');
    
    const headers = new HttpHeaders({
      'Authorization': `Bearer ${token}`
    });

    this.http.delete(`${this.apiUrl}/${id}`, { headers }).subscribe({
      next: (response: any) => {
        console.log('Usuario eliminado:', response);
        this.cargarUsuarios();
        alert('Usuario eliminado exitosamente');
      },
      error: (error) => {
        console.error('Error al eliminar usuario:', error);
        alert('Error al eliminar el usuario: ' + (error.error?.message || 'Intenta nuevamente'));
      }
    });
  }

  crearNuevoUsuario() {
    this.router.navigate(['/usuarios/crear']);
  }

  volverDashboard() {
    this.router.navigate(['/dashboard']);
  }

  formatearFecha(fecha?: string): string {
    if (!fecha) return 'N/A';
    
    const date = new Date(fecha);
    return date.toLocaleDateString('es-ES', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  }
}