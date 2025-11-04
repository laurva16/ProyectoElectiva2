// src/app/dashboard/dashboard.component.ts - ACTUALIZACIÓN AUTOMÁTICA
import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule } from '@angular/router';
import { EstadisticasService } from '../services/estadisticas.service';
import { interval, Subscription } from 'rxjs';

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
  
  // Variables para control de actualizaciones automáticas
  private actualizacionSubscription?: Subscription;
  private readonly INTERVALO_ACTUALIZACION = 30000; // 30 segundos
  
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
    
    // SOLO CARGAR ESTADÍSTICAS SI ES ADMIN
    if (this.isAdmin) {
      console.log('✅ Usuario es ADMIN - Cargando estadísticas...');
      this.cargarEstadisticas();
      this.iniciarActualizacionAutomatica();
    } else {
      console.log('ℹ️ Usuario NO es admin - No se cargan estadísticas');
    }
  }

  ngOnDestroy() {
    // Limpiar suscripción cuando se destruya el componente
    if (this.actualizacionSubscription) {
      this.actualizacionSubscription.unsubscribe();
      console.log('🔴 Actualizaciones automáticas detenidas');
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

  private iniciarActualizacionAutomatica() {
    const intervaloSegundos = this.INTERVALO_ACTUALIZACION / 1000;
    console.log(`🔄 Iniciando actualizaciones automáticas cada ${intervaloSegundos}s`);
    
    // Crear un observable que emita cada X segundos
    this.actualizacionSubscription = interval(this.INTERVALO_ACTUALIZACION).subscribe(() => {
      const ahora = new Date().toLocaleTimeString('es-CO');
      console.log(`⏰ [${ahora}] Actualizando estadísticas automáticamente...`);
      this.cargarEstadisticas(true); // true = actualización silenciosa (sin loader)
    });
  }

  cargarEstadisticas(silencioso: boolean = false) {
    // VERIFICAR QUE SEA ADMIN
    if (!this.isAdmin) {
      console.log('⚠️ No es admin, no se cargan estadísticas');
      return;
    }

    // Solo mostrar loader si NO es actualización silenciosa
    if (!silencioso) {
      this.cargandoEstadisticas = true;
      console.log('📊 Cargando estadísticas (con loader)...');
    } else {
      console.log('📊 Actualizando estadísticas (en segundo plano)...');
    }
    
    this.errorEstadisticas = '';

    this.estadisticasService.obtenerEstadisticasRapidas().subscribe({
      next: (response) => {
        console.log('📥 Respuesta del servidor:', response);
        
        if (response.success && response.data) {
          const estadisticasAnteriores = this.estadisticas;
          this.estadisticas = response.data;
          
          // Comparar valores para detectar cambios (solo si hay estadísticas anteriores Y nuevas)
          if (estadisticasAnteriores && this.estadisticas) {
            const cambioTickets = this.estadisticas.tickets_vendidos_hoy - estadisticasAnteriores.tickets_vendidos_hoy;
            const cambioIngresos = this.estadisticas.ingresos_hoy - estadisticasAnteriores.ingresos_hoy;
            
            if (cambioTickets !== 0 || cambioIngresos !== 0) {
              console.log('🔔 CAMBIOS DETECTADOS:');
              console.log(`   📊 Tickets: ${estadisticasAnteriores.tickets_vendidos_hoy} → ${this.estadisticas.tickets_vendidos_hoy} (${cambioTickets > 0 ? '+' : ''}${cambioTickets})`);
              console.log(`   💰 Ingresos: $${estadisticasAnteriores.ingresos_hoy} → $${this.estadisticas.ingresos_hoy} (${cambioIngresos > 0 ? '+' : ''}$${cambioIngresos})`);
            } else {
              console.log('ℹ️ Sin cambios en las estadísticas');
            }
          }
          
          if (!silencioso) {
            console.log('✅ Estadísticas cargadas correctamente:', this.estadisticas);
          } else {
            console.log('✅ Estadísticas actualizadas en segundo plano');
          }
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
        
        if (!silencioso) {
          this.errorEstadisticas = 'No se pudieron cargar las estadísticas. Intente nuevamente.';
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
    
    // Detener actualizaciones antes de cerrar sesión
    if (this.actualizacionSubscription) {
      this.actualizacionSubscription.unsubscribe();
      console.log('🔴 Actualizaciones detenidas');
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