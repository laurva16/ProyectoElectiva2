import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

const routes: Routes = [
  {
    path: 'listar',
    loadComponent: () => import('./listar-tickets/listar-tickets').then(m => m.ListarTickets)
  },
  {
    path: 'crear',
    loadComponent: () => import('./crear-tickets/crear-tickets').then(m => m.CrearTickets)
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
export class GestionTicketsRoutingModule { }