import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

const routes: Routes = [
  {
    path: 'crear',
    loadComponent: () => import('./crear-usuarios/crear-usuarios').then(m => m.CrearUsuarios)
  },
  {
    path: 'listar',
    loadComponent: () => import('./listar-usuarios/listar-usuarios').then(m => m.ListarUsuarios)
  },
  {
    path: 'editar/:id',
    loadComponent: () => import('./crear-usuarios/crear-usuarios').then(m => m.CrearUsuarios)
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
export class GestionUsuariosRoutingModule { }