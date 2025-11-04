import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

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
    path: 'editar/:id',
    loadComponent: () => import('./editar-peliculas/editar-peliculas').then(m => m.EditarPeliculas)
  },
  {
    path: '',
    redirectTo: 'listar',
    pathMatch: 'full'
  }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class GestionPeliculasRoutingModule { }