import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

const routes: Routes = [
  {
    path: 'listar',
    loadComponent: () => import('./listar-reportes/listar-reportes').then(m => m.ListarReportes)
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
export class GestionReportesRoutingModule { }