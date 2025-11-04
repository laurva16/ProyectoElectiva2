import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

const routes: Routes = [
  {
    path: 'listar',
    loadComponent: () => import('./listar-salas/listar-salas').then(m => m.ListarSalas)
  },
  {
    path: 'crear',
    loadComponent: () => import('./crear-salas/crear-salas').then(m => m.CrearSalas)
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
export class GestionSalasRoutingModule { }