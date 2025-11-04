import { Routes } from '@angular/router';
import { AuthGuard } from './guards/auth.guard';

export const routes: Routes = [
  {
    path: '',
    redirectTo: '/login',
    pathMatch: 'full'
  },
  {
    path: 'login',
    loadComponent: () => import('./autenticacion/login/login').then(m => m.Login),
    title: 'Iniciar Sesión'
  },
  {
    path: 'register',
    loadComponent: () => import('./register/register.component').then(m => m.RegisterComponent),
    title: 'Registro'
  },
  {
    path: 'dashboard',
    loadComponent: () => import('./dashboard/dashboard.component').then(m => m.DashboardComponent),
    canActivate: [AuthGuard],
    title: 'Dashboard'
  },
  // Rutas protegidas con lazy loading
  {
    path: 'peliculas',
    loadChildren: () => import('./gestion-peliculas/gestion-peliculas-module').then(m => m.GestionPeliculasModule),
    canActivate: [AuthGuard],
    title: 'Gestión de Películas'
  },
  {
    path: 'salas',
    loadChildren: () => import('./gestion-salas/gestion-salas-module').then(m => m.GestionSalasModule),
    canActivate: [AuthGuard],
    title: 'Gestión de Salas'
  },
  {
    path: 'tickets',
    loadChildren: () => import('./gestion-tickets/gestion-tickets-module').then(m => m.GestionTicketsModule),
    canActivate: [AuthGuard],
    title: 'Gestión de Tickets'
  },
  {
    path: 'usuarios',
    loadChildren: () => import('./gestion-usuarios/gestion-usuarios-module').then(m => m.GestionUsuariosModule),
    canActivate: [AuthGuard],
    title: 'Gestión de Usuarios'
  },
  {
    path: 'reportes',
    loadChildren: () => import('./gestion-reportes/gestion-reportes-module').then(m => m.GestionReportesModule),
    canActivate: [AuthGuard],
    title: 'Reportes'
  },
  {
    path: '**',
    redirectTo: '/login'
  }
];