
// ============================================
// ARCHIVO 1: src/app/dashboard/dashboard.component.ts
// ============================================
import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule } from '@angular/router';
import { EstadisticasService } from '../services/estadisticas.service';
import { Subscription } from 'rxjs';

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
export class DashboardComponent implements OnInit, OnDestroy {
  currentUser: any = null;
  sidebarCollapsed: boolean = false;
  estadisticas: Estadisticas | null = null;
  cargandoEstadisticas: boolean = false;
  errorEstadisticas: string = '';
  Math = Math;
  
  private cargarSubscription?: Subscription;
  
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
    console.log('🚀 Inicializando Dashboard...');
    this.loadCurrentUser();
    
    if (this.isAdmin) {
      console.log('✅ Usuario es ADMIN - Intentando cargar estadísticas...');
      this.cargarEstadisticas();
    } else {
      console.log('ℹ️ Usuario NO es admin - No se cargan estadísticas');
    }
  }

  ngOnDestroy() {
    if (this.cargarSubscription) {
      this.cargarSubscription.unsubscribe();
      console.log('🔴 Suscripción de estadísticas cancelada');
    }
  }

  private loadCurrentUser() {
    const userData = localStorage.getItem('cinemax_user') || 
                    sessionStorage.getItem('cinemax_user');
    
    if (userData) {
      this.currentUser = JSON.parse(userData);
      console.log('👤 Usuario cargado:', {
        nombre: this.currentUser.name,
        role: this.currentUser.role,
        esAdmin: this.isAdmin
      });
    } else {
      console.warn('⚠️ No se encontró información del usuario');
    }
  }

  cargarEstadisticas() {
    if (!this.isAdmin) {
      console.log('⚠️ No es admin, no se cargan estadísticas');
      return;
    }

    this.cargandoEstadisticas = true;
    this.errorEstadisticas = '';
    console.log('📊 Cargando estadísticas...');

    this.cargarSubscription = this.estadisticasService.obtenerEstadisticasRapidas().subscribe({
      next: (response) => {
        console.log('📥 Respuesta del servidor:', response);
        
        if (response.success && response.data) {
          this.estadisticas = response.data;
          console.log('✅ Estadísticas cargadas:', this.estadisticas);
        } else {
          this.errorEstadisticas = response.message || 'Error al cargar estadísticas';
          console.error('❌ Error en respuesta:', this.errorEstadisticas);
        }
        this.cargandoEstadisticas = false;
      },
      error: (error) => {
        console.error('❌ Error al cargar estadísticas:', error);
        console.error('   Status:', error.status);
        console.error('   Mensaje:', error.message);
        
        // Manejo mejorado: SI EL ENDPOINT NO EXISTE (404), NO MOSTRAR ERROR MOLESTO
        if (error.status === 404) {
          console.warn('⚠️ Endpoint de estadísticas no disponible en el backend');
          this.errorEstadisticas = '';
          // Datos de fallback
          this.estadisticas = {
            total_peliculas: 0,
            tickets_vendidos_hoy: 0,
            ingresos_hoy: 0,
            total_salas: 0,
            total_usuarios: 0
          };
        } else {
          this.errorEstadisticas = 'No se pudieron cargar las estadísticas.';
        }
        
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
    console.log('👋 Cerrando sesión...');
    
    if (this.cargarSubscription) {
      this.cargarSubscription.unsubscribe();
      console.log('🔴 Carga cancelada');
    }
    
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