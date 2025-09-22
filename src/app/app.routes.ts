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
    loadComponent: () => import('./autenticacion/login/login').then(m => m.Login)
  },
  {
    path: 'register',
    loadComponent: () => import('./register/register.component').then(m => m.RegisterComponent)
  },
  {
    path: 'dashboard',
    loadComponent: () => import('./dashboard/dashboard.component').then(m => m.DashboardComponent),
    canActivate: [AuthGuard]  // Proteger la ruta con el guard
  },
  // Rutas protegidas adicionales
  {
    path: 'peliculas',
    loadChildren: () => import('./gestion-peliculas/gestion-peliculas-module').then(m => m.GestionPeliculasModule),
    canActivate: [AuthGuard]
  },
  {
    path: 'salas',
    loadChildren: () => import('./gestion-salas/gestion-salas-module').then(m => m.GestionSalasModule),
    canActivate: [AuthGuard]
  },
  {
    path: 'tickets',
    loadChildren: () => import('./gestion-tickets/gestion-tickets-module').then(m => m.GestionTicketsModule),
    canActivate: [AuthGuard]
  },
  {
    path: 'usuarios',
    loadChildren: () => import('./gestion-usuarios/gestion-usuarios-module').then(m => m.GestionUsuariosModule),
    canActivate: [AuthGuard]
  },
  {
    path: 'reportes',
    loadChildren: () => import('./gestion-reportes/gestion-reportes-module').then(m => m.GestionReportesModule),
    canActivate: [AuthGuard]
  },
  {
    path: '**',
    redirectTo: '/login'  // Redirigir rutas no encontradas al login
  }
];