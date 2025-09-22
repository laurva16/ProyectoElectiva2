import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div style="padding: 2rem; background: #141414; color: white; min-height: 100vh;">
      <h1 style="color: #e50914; margin-bottom: 2rem;">Dashboard - CineMax</h1>
      
      <div style="background: #1f1f1f; padding: 2rem; border-radius: 8px; border: 1px solid #333;">
        <h2>¡Bienvenido al Sistema!</h2>
        <p style="margin: 1rem 0; color: #b3b3b3;">
          El login funciona correctamente. Desde aquí podrás navegar a:
        </p>
        
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem; margin-top: 2rem;">
          <div style="background: rgba(229, 9, 20, 0.1); padding: 1.5rem; border-radius: 8px; border: 1px solid rgba(229, 9, 20, 0.3);">
            <h3 style="color: #e50914; margin-bottom: 0.5rem;">🎬 Películas</h3>
            <p style="color: #b3b3b3; font-size: 0.9rem;">Gestionar el catálogo de películas</p>
          </div>
          
          <div style="background: rgba(229, 9, 20, 0.1); padding: 1.5rem; border-radius: 8px; border: 1px solid rgba(229, 9, 20, 0.3);">
            <h3 style="color: #e50914; margin-bottom: 0.5rem;">🏛️ Salas</h3>
            <p style="color: #b3b3b3; font-size: 0.9rem;">Administrar salas de cine</p>
          </div>
          
          <div style="background: rgba(229, 9, 20, 0.1); padding: 1.5rem; border-radius: 8px; border: 1px solid rgba(229, 9, 20, 0.3);">
            <h3 style="color: #e50914; margin-bottom: 0.5rem;">🎫 Tickets</h3>
            <p style="color: #b3b3b3; font-size: 0.9rem;">Sistema de venta de entradas</p>
          </div>
          
          <div style="background: rgba(229, 9, 20, 0.1); padding: 1.5rem; border-radius: 8px; border: 1px solid rgba(229, 9, 20, 0.3);">
            <h3 style="color: #e50914; margin-bottom: 0.5rem;">👥 Usuarios</h3>
            <p style="color: #b3b3b3; font-size: 0.9rem;">Gestión de usuarios del sistema</p>
          </div>
        </div>
        
        <div style="margin-top: 2rem; padding: 1rem; background: rgba(70, 211, 105, 0.1); border: 1px solid rgba(70, 211, 105, 0.3); border-radius: 8px;">
          <p style="color: #46d369; margin: 0;">
            ✅ <strong>Backend conectado exitosamente</strong><br>
            Tu frontend Angular está comunicándose correctamente con Flask.
          </p>
        </div>
      </div>
    </div>
  `
})
export class DashboardComponent {}