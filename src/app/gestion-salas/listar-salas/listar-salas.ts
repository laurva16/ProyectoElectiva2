import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { SalasService } from '../../services/salas.service';

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

  // Usuario actual
  currentUser: any = null;

  // Getter para verificar si es admin
  get isAdmin(): boolean {
    return this.currentUser?.role === 'admin';
  }

  constructor(
    private salasService: SalasService,
    private router: Router
  ) {}

  ngOnInit() {
    this.loadCurrentUser();
    this.cargarSalas();
  }

  private loadCurrentUser() {
    const userData = localStorage.getItem('cinemax_user') || 
                    sessionStorage.getItem('cinemax_user');
    
    if (userData) {
      this.currentUser = JSON.parse(userData);
    }
  }

  cargarSalas() {
    this.loading = true;

    this.salasService.obtenerSalas().subscribe({
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
    // Verificar permisos antes de eliminar
    if (!this.isAdmin) {
      alert('No tienes permisos para eliminar salas');
      return;
    }

    if (!confirm(`¿Estás seguro de eliminar la sala "${sala.nombre}"?`)) {
      return;
    }

    this.salasService.eliminarSala(sala.id).subscribe({
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
    // Verificar permisos antes de navegar
    if (!this.isAdmin) {
      alert('No tienes permisos para crear salas');
      return;
    }
    
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