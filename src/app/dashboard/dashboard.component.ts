// src/app/dashboard/dashboard.component.ts
import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule } from '@angular/router';
import { EstadisticasService } from '../services/estadisticas.service';

interface ModuleCard {
  title: string;
  description: string;
  icon: string;
  route: string;
  color: string;
  adminOnly?: boolean;
}

interface Estadisticas {
  total_peliculas: number;
  tickets_vendidos_hoy: number;
  ingresos_hoy: number;
  total_salas: number;
  total_usuarios: number;
  cambio_tickets?: number;
}

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.css']
})
export class DashboardComponent implements OnInit {
  currentUser: any = null;
  sidebarCollapsed: boolean = false;
  estadisticas: Estadisticas | null = null;
  cargandoEstadisticas: boolean = false;
  errorEstadisticas: string = '';
  Math = Math;
  
  get isAdmin(): boolean {
    return this.currentUser?.role === 'admin';
  }
  
  private allModules: ModuleCard[] = [
    {
      title: 'Películas',
      description: 'Gestiona el catálogo completo de películas',
      icon: 'fas fa-film',
      route: '/peliculas/listar',
      color: '#e50914'
    },
    {
      title: 'Salas',
      description: 'Administra las salas de cine',
      icon: 'fas fa-theater-masks',
      route: '/salas/listar',
      color: '#46d369'
    },
    {
      title: 'Tickets',
      description: 'Sistema de venta de entradas',
      icon: 'fas fa-ticket-alt',
      route: '/tickets/listar',
      color: '#3b82f6'
    },
    {
      title: 'Usuarios',
      description: 'Gestión de usuarios del sistema',
      icon: 'fas fa-users',
      route: '/usuarios/listar',
      color: '#ffa500',
      adminOnly: true
    },
    {
      title: 'Reportes',
      description: 'Estadísticas y reportes del negocio',
      icon: 'fas fa-chart-bar',
      route: '/reportes/listar',
      color: '#9333ea',
      adminOnly: true
    }
  ];

  get visibleModules(): ModuleCard[] {
    if (this.isAdmin) {
      return this.allModules;
    }
    return this.allModules.filter(module => !module.adminOnly);
  }

  constructor(
    private router: Router,
    private estadisticasService: EstadisticasService
  ) {}

  ngOnInit() {
    this.loadCurrentUser();
    this.cargarEstadisticas();
  }

  private loadCurrentUser() {
    const userData = localStorage.getItem('cinemax_user') || 
                    sessionStorage.getItem('cinemax_user');
    
    if (userData) {
      this.currentUser = JSON.parse(userData);
    }
  }

  cargarEstadisticas() {
    this.cargandoEstadisticas = true;
    this.errorEstadisticas = '';

    this.estadisticasService.obtenerEstadisticasRapidas().subscribe({
      next: (response) => {
        if (response.success) {
          this.estadisticas = response.data;
        } else {
          this.errorEstadisticas = response.message || 'Error al cargar estadísticas';
        }
        this.cargandoEstadisticas = false;
      },
      error: (error) => {
        console.error('Error al cargar estadísticas:', error);
        this.errorEstadisticas = 'No se pudieron cargar las estadísticas. Intente nuevamente.';
        this.cargandoEstadisticas = false;
      }
    });
  }

  formatearPrecio(precio: number): string {
    return precio.toLocaleString('es-CO', {
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    });
  }

  obtenerHoraActual(): string {
    const ahora = new Date();
    return ahora.toLocaleTimeString('es-CO', {
      hour: '2-digit',
      minute: '2-digit'
    });
  }

  navigateTo(route: string) {
    this.router.navigate([route]);
  }

  logout() {
    localStorage.removeItem('cinemax_token');
    localStorage.removeItem('cinemax_user');
    sessionStorage.removeItem('cinemax_token');
    sessionStorage.removeItem('cinemax_user');
    this.router.navigate(['/login']);
  }
  
  toggleSidebar() {
    this.sidebarCollapsed = !this.sidebarCollapsed;
  }
}