import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule } from '@angular/router';

interface ModuleCard {
  title: string;
  description: string;
  icon: string;
  route: string;
  color: string;
  adminOnly?: boolean;
}

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, RouterModule],
  template: `
    <div class="dashboard-container">
      <!-- Sidebar -->
      <aside class="sidebar" [class.collapsed]="sidebarCollapsed">
        <div class="logo">
          <i class="fas fa-film"></i>
          <span *ngIf="!sidebarCollapsed">CineMax</span>
        </div>
        
        <nav class="sidebar-nav">
          <a class="nav-item active">
            <i class="fas fa-home"></i>
            <span *ngIf="!sidebarCollapsed">Dashboard</span>
          </a>
          <a class="nav-item" [routerLink]="['/peliculas/listar']">
            <i class="fas fa-film"></i>
            <span *ngIf="!sidebarCollapsed">Películas</span>
          </a>
          <a class="nav-item" [routerLink]="['/salas/listar']">
            <i class="fas fa-theater-masks"></i>
            <span *ngIf="!sidebarCollapsed">Salas</span>
          </a>
          <a class="nav-item" [routerLink]="['/tickets/listar']">
            <i class="fas fa-ticket-alt"></i>
            <span *ngIf="!sidebarCollapsed">Tickets</span>
          </a>
          <a *ngIf="currentUser?.role === 'admin'" class="nav-item" [routerLink]="['/usuarios/listar']">
            <i class="fas fa-users"></i>
            <span *ngIf="!sidebarCollapsed">Usuarios</span>
          </a>
          <a *ngIf="currentUser?.role === 'admin'" class="nav-item" [routerLink]="['/reportes/listar']">
            <i class="fas fa-chart-bar"></i>
            <span *ngIf="!sidebarCollapsed">Reportes</span>
          </a>
        </nav>

        <div class="sidebar-footer">
          <button class="btn-settings">
            <i class="fas fa-cog"></i>
          </button>
        </div>
      </aside>

      <!-- Main Content -->
      <main class="main-content" [class.expanded]="sidebarCollapsed">
        <!-- Header -->
        <header class="header">
          <div class="header-left">
            <button class="toggle-sidebar-btn" (click)="toggleSidebar()">
              <i class="fas" [class.fa-bars]="sidebarCollapsed" [class.fa-times]="!sidebarCollapsed"></i>
            </button>
            <div class="search-bar">
            <i class="fas fa-search"></i>
            <input type="text" placeholder="Buscar películas, salas, tickets...">
          </div>
          </div>
        
          
          <div class="header-actions">
            <button class="notification-btn">
              <i class="fas fa-bell"></i>
              <span class="badge">3</span>
            </button>
            
            <div class="user-menu">
              <div class="user-info">
                <span class="user-name">{{ currentUser?.name }}</span>
                <span class="user-role">{{ currentUser?.role === 'admin' ? 'Administrador' : 'Empleado' }}</span>
              </div>
              <img src="https://ui-avatars.com/api/?name={{ currentUser?.name }}&background=e50914&color=fff" alt="Avatar">
              <button (click)="logout()" class="btn-logout" title="Cerrar sesión">
                <i class="fas fa-sign-out-alt"></i>
              </button>
            </div>
          </div>
        </header>

        <!-- Hero Section -->
        <section class="hero-section">
          <div class="hero-content">
            <span class="hero-badge">
              <i class="fas fa-fire"></i> Bienvenido
            </span>
            <h1 class="hero-title">Panel de Control</h1>
            <p class="hero-description">
              Gestiona todas las operaciones del cine desde un solo lugar
            </p>
          </div>
          <div class="hero-image">
            <i class="fas fa-film"></i>
          </div>
        </section>

        <!-- Módulos Grid -->
        <section class="modules-section">
          <div class="section-header">
            <h2>Módulos del Sistema</h2>
            <p>Accede rápidamente a las funcionalidades principales</p>
          </div>

          <div class="modules-grid">
            <div *ngFor="let module of modules" 
                 class="module-card"
                 [class.admin-only]="module.adminOnly && currentUser?.role !== 'admin'"
                 [style.--module-color]="module.color"
                 (click)="navigateTo(module.route)"
                 [class.disabled]="module.adminOnly && currentUser?.role !== 'admin'">
              <div class="module-icon">
                <i [class]="module.icon"></i>
              </div>
              <div class="module-info">
                <h3>{{ module.title }}</h3>
                <p>{{ module.description }}</p>
              </div>
              <button class="module-action">
                <i class="fas fa-arrow-right"></i>
              </button>
              <div *ngIf="module.adminOnly && currentUser?.role !== 'admin'" class="admin-badge">
                <i class="fas fa-lock"></i>
              </div>
            </div>
          </div>
        </section>

        <!-- Stats Section -->
        <section class="stats-section">
          <div class="section-header">
            <h2>Estadísticas Rápidas</h2>
          </div>
          
          <div class="stats-grid">
            <div class="stat-card">
              <div class="stat-icon" style="background: rgba(229, 9, 20, 0.1);">
                <i class="fas fa-film" style="color: #e50914;"></i>
              </div>
              <div class="stat-info">
                <span class="stat-value">24</span>
                <span class="stat-label">Películas en Cartelera</span>
              </div>
            </div>

            <div class="stat-card">
              <div class="stat-icon" style="background: rgba(70, 211, 105, 0.1);">
                <i class="fas fa-ticket-alt" style="color: #46d369;"></i>
              </div>
              <div class="stat-info">
                <span class="stat-value">156</span>
                <span class="stat-label">Tickets Vendidos Hoy</span>
              </div>
            </div>

            <div class="stat-card">
              <div class="stat-icon" style="background: rgba(255, 165, 0, 0.1);">
                <i class="fas fa-theater-masks" style="color: #ffa500;"></i>
              </div>
              <div class="stat-info">
                <span class="stat-value">8</span>
                <span class="stat-label">Salas Activas</span>
              </div>
            </div>

            <div class="stat-card">
              <div class="stat-icon" style="background: rgba(59, 130, 246, 0.1);">
                <i class="fas fa-users" style="color: #3b82f6;"></i>
              </div>
              <div class="stat-info">
                <span class="stat-value">342</span>
                <span class="stat-label">Usuarios Registrados</span>
              </div>
            </div>
          </div>
        </section>
      </main>
    </div>
  `,
  styles: [`
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }

    .dashboard-container {
      display: flex;
      min-height: 100vh;
      background: #0a0a0a;
      color: #ffffff;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
    }

    /* Sidebar */
    .sidebar {
      width: 260px;
      background: #141414;
      border-right: 1px solid #2a2a2a;
      display: flex;
      flex-direction: column;
      position: fixed;
      height: 100vh;
      left: 0;
      top: 0;
    }
    .sidebar.collapsed {
      width: 80px;
    }

    .logo {
      padding: 1.5rem;
      display: flex;
      align-items: center;
      gap: 0.75rem;
      font-size: 1.5rem;
      font-weight: 700;
      color: #e50914;
      border-bottom: 1px solid #2a2a2a;
      justify-content: center;
    }

    .sidebar-nav {
      flex: 1;
      padding: 1rem 0;
      overflow-y: auto;
    }

    .nav-item {
      display: flex;
      align-items: center;
      gap: 0.75rem;
      padding: 0.875rem 1.5rem;
      color: #a0a0a0;
      text-decoration: none;
      transition: all 0.2s;
      cursor: pointer;
      border-left: 3px solid transparent;
      white-space: nowrap;
    }
    .sidebar.collapsed .nav-item {
      justify-content: center;
      padding: 0.875rem 0.5rem;
    }

    .nav-item:hover {
      background: rgba(229, 9, 20, 0.1);
      color: #ffffff;
      border-left-color: #e50914;
    }

    .nav-item.active {
      background: rgba(229, 9, 20, 0.15);
      color: #e50914;
      border-left-color: #e50914;
    }

    .nav-item i {
      font-size: 1.25rem;
      width: 1.5rem;
      text-align: center;
    }

    .sidebar-footer {
      padding: 1rem 1.5rem;
      border-top: 1px solid #2a2a2a;
    }

    .btn-settings {
      width: 100%;
      padding: 0.75rem;
      background: transparent;
      border: 1px solid #2a2a2a;
      color: #a0a0a0;
      border-radius: 8px;
      cursor: pointer;
      transition: all 0.2s;
      font-size: 1.25rem;
    }

    .btn-settings:hover {
      background: rgba(229, 9, 20, 0.1);
      border-color: #e50914;
      color: #e50914;
    }

    /* Main Content */
    .main-content {
      flex: 1;
      margin-left: 260px;
      overflow-y: auto;
      transition: margin-left 0.3s ease;
    }
    .main-content.expanded {
      margin-left: 80px;
    }
    /* Header */
    .header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 1.5rem 2rem;
      background: #141414;
      border-bottom: 1px solid #2a2a2a;
      position: sticky;
      top: 0;
      z-index: 10;
    }

    .search-bar {
      display: flex;
      align-items: center;
      gap: 0.75rem;
      background: #1f1f1f;
      padding: 0.75rem 1.25rem;
      border-radius: 12px;
      flex: 1;
      max-width: 500px;
      border: 1px solid #2a2a2a;
    }

    .search-bar i {
      color: #666;
    }

    .search-bar input {
      flex: 1;
      background: transparent;
      border: none;
      outline: none;
      color: #ffffff;
      font-size: 0.95rem;
    }

    .header-actions {
      display: flex;
      align-items: center;
      gap: 1.5rem;
    }

    .notification-btn {
      position: relative;
      background: #1f1f1f;
      border: 1px solid #2a2a2a;
      color: #a0a0a0;
      width: 40px;
      height: 40px;
      border-radius: 10px;
      cursor: pointer;
      transition: all 0.2s;
    }

    .notification-btn:hover {
      background: rgba(229, 9, 20, 0.1);
      border-color: #e50914;
      color: #e50914;
    }

    .notification-btn .badge {
      position: absolute;
      top: -5px;
      right: -5px;
      background: #e50914;
      color: white;
      width: 18px;
      height: 18px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 0.7rem;
      font-weight: 600;
    }

    .user-menu {
      display: flex;
      align-items: center;
      gap: 1rem;
      padding: 0.5rem;
      background: #1f1f1f;
      border: 1px solid #2a2a2a;
      border-radius: 12px;
    }

    .user-info {
      display: flex;
      flex-direction: column;
      align-items: flex-end;
    }

    .user-name {
      font-weight: 600;
      font-size: 0.9rem;
    }

    .user-role {
      font-size: 0.75rem;
      color: #666;
    }

    .user-menu img {
      width: 40px;
      height: 40px;
      border-radius: 10px;
    }

    .btn-logout {
      background: transparent;
      border: none;
      color: #a0a0a0;
      cursor: pointer;
      padding: 0.5rem;
      transition: color 0.2s;
      font-size: 1.1rem;
    }

    .btn-logout:hover {
      color: #e50914;
    }

    /* Hero Section */
    .hero-section {
      background: linear-gradient(135deg, #1f1f1f 0%, #141414 100%);
      padding: 3rem 2rem;
      margin: 2rem;
      border-radius: 20px;
      border: 1px solid #2a2a2a;
      display: flex;
      justify-content: space-between;
      align-items: center;
      position: relative;
      overflow: hidden;
    }

    .hero-section::before {
      content: '';
      position: absolute;
      top: 0;
      right: 0;
      width: 50%;
      height: 100%;
      background: radial-gradient(circle at center, rgba(229, 9, 20, 0.1) 0%, transparent 70%);
      pointer-events: none;
    }

    .hero-content {
      z-index: 1;
    }

    .hero-badge {
      display: inline-flex;
      align-items: center;
      gap: 0.5rem;
      padding: 0.5rem 1rem;
      background: rgba(229, 9, 20, 0.15);
      border: 1px solid rgba(229, 9, 20, 0.3);
      color: #e50914;
      border-radius: 20px;
      font-size: 0.85rem;
      font-weight: 600;
      margin-bottom: 1rem;
    }

    .hero-title {
      font-size: 2.5rem;
      font-weight: 700;
      margin-bottom: 0.5rem;
    }

    .hero-description {
      color: #a0a0a0;
      font-size: 1.1rem;
    }

    .hero-image {
      font-size: 8rem;
      color: rgba(229, 9, 20, 0.2);
      z-index: 1;
    }

    /* Modules Section */
    .modules-section {
      padding: 2rem;
    }

    .section-header {
      margin-bottom: 2rem;
    }

    .section-header h2 {
      font-size: 1.75rem;
      margin-bottom: 0.5rem;
    }

    .section-header p {
      color: #666;
    }

    .modules-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
      gap: 1.5rem;
    }

    .module-card {
      background: #141414;
      border: 1px solid #2a2a2a;
      border-radius: 16px;
      padding: 1.5rem;
      cursor: pointer;
      transition: all 0.3s ease;
      display: flex;
      gap: 1rem;
      align-items: start;
      position: relative;
      overflow: hidden;
    }

    .module-card::before {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      width: 4px;
      height: 100%;
      background: var(--module-color);
      transform: scaleY(0);
      transition: transform 0.3s ease;
    }

    .module-card:hover::before {
      transform: scaleY(1);
    }

    .module-card:hover {
      transform: translateY(-5px);
      border-color: var(--module-color);
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
    }

    .module-card.disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }

    .module-icon {
      width: 50px;
      height: 50px;
      border-radius: 12px;
      background: rgba(229, 9, 20, 0.1);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 1.5rem;
      color: var(--module-color);
      flex-shrink: 0;
    }

    .module-info {
      flex: 1;
    }

    .module-info h3 {
      font-size: 1.1rem;
      margin-bottom: 0.5rem;
    }

    .module-info p {
      color: #666;
      font-size: 0.9rem;
    }

    .module-action {
      background: rgba(229, 9, 20, 0.1);
      border: none;
      width: 36px;
      height: 36px;
      border-radius: 8px;
      color: var(--module-color);
      cursor: pointer;
      transition: all 0.2s;
    }

    .module-action:hover {
      background: var(--module-color);
      color: white;
    }

    .admin-badge {
      position: absolute;
      top: 1rem;
      right: 1rem;
      background: rgba(255, 165, 0, 0.2);
      color: #ffa500;
      padding: 0.25rem 0.5rem;
      border-radius: 6px;
      font-size: 0.75rem;
    }

    /* Stats Section */
    .stats-section {
      padding: 2rem;
    }

    .stats-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
      gap: 1.5rem;
    }

    .stat-card {
      background: #141414;
      border: 1px solid #2a2a2a;
      border-radius: 16px;
      padding: 1.5rem;
      display: flex;
      align-items: center;
      gap: 1rem;
    }

    .stat-icon {
      width: 60px;
      height: 60px;
      border-radius: 12px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 1.75rem;
    }

    .stat-info {
      display: flex;
      flex-direction: column;
    }

    .stat-value {
      font-size: 2rem;
      font-weight: 700;
    }

    .stat-label {
      color: #666;
      font-size: 0.85rem;
    }
        .header-left {
      display: flex;
      align-items: center;
      gap: 1rem;
      flex: 1;
      max-width: 600px;
    }

    .toggle-sidebar-btn {
      background: #1f1f1f;
      border: 1px solid #2a2a2a;
      color: #a0a0a0;
      width: 40px;
      height: 40px;
      border-radius: 10px;
      cursor: pointer;
      transition: all 0.2s;
      font-size: 1.1rem;
    }

    .toggle-sidebar-btn:hover {
      background: rgba(229, 9, 20, 0.1);
      border-color: #e50914;
      color: #e50914;
    }
  `]
})
export class DashboardComponent implements OnInit {
  currentUser: any = null;
  sidebarCollapsed: boolean = false;
  
  modules: ModuleCard[] = [
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

  constructor(private router: Router) {}

  ngOnInit() {
    this.loadCurrentUser();
  }

  private loadCurrentUser() {
    const userData = localStorage.getItem('cinemax_user') || 
                    sessionStorage.getItem('cinemax_user');
    
    if (userData) {
      this.currentUser = JSON.parse(userData);
    }
  }

  navigateTo(route: string) {
    const module = this.modules.find(m => m.route === route);
    if (module?.adminOnly && this.currentUser?.role !== 'admin') {
      return;
    }
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