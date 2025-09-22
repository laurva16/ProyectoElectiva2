import { Routes } from '@angular/router';

export const routes: Routes = [
  // Ruta por defecto - redirige a login
  { 
    path: '', 
    redirectTo: '/login', 
    pathMatch: 'full' 
  },

  // Autenticación
  { 
    path: 'login', 
    loadComponent: () => import('./autenticacion/login/login').then(m => m.Login)
  },

  // Dashboard temporal - puedes crear este componente después
  {
    path: 'dashboard',
    loadComponent: () => import('./dashboard/dashboard.component').then(m => m.DashboardComponent)
  },

  // Gestión de Películas - comentadas hasta que crees los componentes
  /*
  { 
    path: 'peliculas', 
    loadComponent: () => import('./gestion-peliculas/listar-peliculas/listar-peliculas').then(m => m.ListarPeliculas)
  },
  { 
    path: 'peliculas/crear', 
    loadComponent: () => import('./gestion-peliculas/crear-peliculas/crear-peliculas').then(m => m.CrearPeliculas)
  },
  */

  // Ruta wildcard - para páginas no encontradas
  {
    path: '**',
    redirectTo: '/login'
  }
];