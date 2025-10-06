import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule } from '@angular/router';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { FormsModule } from '@angular/forms';

interface Sala {
  id: number;
  nombre: string;
  capacidad: number;
  tipo: string;
  tecnologia: string;
  estado: string;
  precio_base: number;
  filas: number;
  asientos_por_fila: number;
  descripcion?: string;
  created_at?: string;
  updated_at?: string;
}

@Component({
  selector: 'app-listar-salas',
  standalone: true,
  imports: [CommonModule, RouterModule, FormsModule],
  templateUrl: './listar-salas.html',
  styleUrl: './listar-salas.css'
})
export class ListarSalas implements OnInit {
  salas: Sala[] = [];
  salasFiltradas: Sala[] = [];
  loading = true;
  
  // Filtros
  searchTerm = '';
  filtroTipo = '';
  filtroEstado = '';
  
  // Modal
  showModal = false;
  salaSeleccionada: Sala | null = null;

  private apiUrl = 'http://localhost:5000/api/salas';

  constructor(
    private http: HttpClient,
    private router: Router
  ) {}

  ngOnInit() {
    this.cargarSalas();
  }

  cargarSalas() {
    this.loading = true;
    
    const token = localStorage.getItem('cinemax_token') || sessionStorage.getItem('cinemax_token');
    
    const headers = new HttpHeaders({
      'Authorization': `Bearer ${token}`
    });

    this.http.get<any>(this.apiUrl, { headers }).subscribe({
      next: (response) => {
        this.loading = false;
        if (response.success) {
          this.salas = response.data;
          this.aplicarFiltros();
        }
      },
      error: (error) => {
        this.loading = false;
        console.error('Error al cargar salas:', error);
        
        if (error.status === 401) {
          this.router.navigate(['/login']);
        }
      }
    });
  }

  aplicarFiltros() {
    this.salasFiltradas = this.salas.filter(sala => {
      const cumpleBusqueda = sala.nombre.toLowerCase().includes(this.searchTerm.toLowerCase()) ||
                             sala.descripcion?.toLowerCase().includes(this.searchTerm.toLowerCase());
      
      const cumpleTipo = !this.filtroTipo || sala.tipo === this.filtroTipo;
      const cumpleEstado = !this.filtroEstado || sala.estado === this.filtroEstado;
      
      return cumpleBusqueda && cumpleTipo && cumpleEstado;
    });
  }

  onSearchChange() {
    this.aplicarFiltros();
  }

  onFiltroTipoChange() {
    this.aplicarFiltros();
  }

  onFiltroEstadoChange() {
    this.aplicarFiltros();
  }

  limpiarFiltros() {
    this.searchTerm = '';
    this.filtroTipo = '';
    this.filtroEstado = '';
    this.aplicarFiltros();
  }

  verDetalle(sala: Sala) {
    this.salaSeleccionada = sala;
    this.showModal = true;
  }

  cerrarModal() {
    this.showModal = false;
    this.salaSeleccionada = null;
  }

  eliminarSala(sala: Sala) {
    if (!confirm(`¿Estás seguro de eliminar la sala "${sala.nombre}"?`)) {
      return;
    }

    const token = localStorage.getItem('cinemax_token') || sessionStorage.getItem('cinemax_token');
    
    const headers = new HttpHeaders({
      'Authorization': `Bearer ${token}`
    });

    this.http.delete(`${this.apiUrl}/${sala.id}`, { headers }).subscribe({
      next: (response: any) => {
        if (response.success) {
          this.salas = this.salas.filter(s => s.id !== sala.id);
          this.aplicarFiltros();
          alert('Sala eliminada exitosamente');
        }
      },
      error: (error) => {
        console.error('Error al eliminar sala:', error);
        alert(error.error?.message || 'Error al eliminar la sala');
      }
    });
  }

  crearNuevaSala() {
    this.router.navigate(['/salas/crear']);
  }

  volver() {
    this.router.navigate(['/dashboard']);
  }

  getIconoTipo(tipo: string): string {
    const iconos: { [key: string]: string } = {
      'VIP': 'fa-crown',
      'IMAX': 'fa-expand',
      'Premium': 'fa-star',
      '4DX': 'fa-cube',
      'Estándar': 'fa-film'
    };
    return iconos[tipo] || 'fa-film';
  }

  getClaseTipo(tipo: string): string {
    const clases: { [key: string]: string } = {
      'VIP': 'vip',
      'IMAX': 'imax',
      'Premium': 'premium',
      '4DX': '4dx',
      'Estándar': 'standard'
    };
    return clases[tipo] || 'standard';
  }
}