import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Routes } from '@angular/router';

// Define las rutas del módulo
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
  imports: [
    CommonModule,
    RouterModule.forChild(routes)
  ]
})
export class GestionSalasModule { }