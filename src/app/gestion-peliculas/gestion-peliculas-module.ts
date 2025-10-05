import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Routes } from '@angular/router';

// Define las rutas del módulo
const routes: Routes = [
  {
    path: 'listar',
    loadComponent: () => import('./listar-peliculas/listar-peliculas').then(m => m.ListarPeliculas)
  },
  {
    path: 'crear',
    loadComponent: () => import('./crear-peliculas/crear-peliculas').then(m => m.CrearPeliculas)
  },
  {
    path: '',
    redirectTo: 'listar',
    pathMatch: 'full'
  }
];

@NgModule({
  imports: [
    CommonModule,
    RouterModule.forChild(routes)
  ]
})
export class GestionPeliculasModule { }