import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule } from '@angular/router';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, RouterModule],
  template: `
    <div style="padding: 2rem; background: #141414; color: white; min-height: 100vh;">
      <!-- Header con información del usuario y logout -->
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem; padding: 1rem; background: #1f1f1f; border-radius: 8px; border: 1px solid #333;">
        <div>
          <h1 style="color: #e50914; margin: 0;">Dashboard - CineMax</h1>
          <p style="margin: 0.5rem 0 0 0; color: #b3b3b3;">Bienvenido, {{ currentUser?.name }}</p>
        </div>
        <div style="display: flex; align-items: center; gap: 1rem;">
          <div style="text-align: right;">
            <div style="color: #ffffff; font-weight: 500;">{{ currentUser?.name }}</div>
            <div style="color: #b3b3b3; font-size: 0.85rem;">{{ currentUser?.role === 'admin' ? 'Administrador' : 'Empleado' }}</div>
          </div>
          <button 
            (click)="logout()" 
            style="background: #e50914; color: white; border: none; padding: 0.5rem 1rem; border-radius: 6px; cursor: pointer; display: flex; align-items: center; gap: 0.5rem; transition: background 0.3s ease;"
            onmouseover="this.style.background='#b8070f'" 
            onmouseout="this.style.background='#e50914'"
          >
            <i class="fas fa-sign-out-alt"></i>
            Cerrar Sesión
          </button>
        </div>
      </div>
      
      <div style="background: #1f1f1f; padding: 2rem; border-radius: 8px; border: 1px solid #333;">
        <h2>Panel de Control</h2>
        <p style="margin: 1rem 0; color: #b3b3b3;">
          Desde aquí puedes navegar a las diferentes secciones del sistema:
        </p>
        
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem; margin-top: 2rem;">
          <div 
            style="background: rgba(229, 9, 20, 0.1); padding: 1.5rem; border-radius: 8px; border: 1px solid rgba(229, 9, 20, 0.3); cursor: pointer; transition: all 0.3s ease;"
            onmouseover="this.style.transform='translateY(-5px)'; this.style.boxShadow='0 10px 25px rgba(229, 9, 20, 0.2)'"
            onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='none'"
          >
            <h3 style="color: #e50914; margin-bottom: 0.5rem; display: flex; align-items: center; gap: 0.5rem;">
              <i class="fas fa-film"></i> Películas
            </h3>
            <p style="color: #b3b3b3; font-size: 0.9rem;">Gestionar el catálogo de películas</p>
          </div>
          
          <div 
            style="background: rgba(229, 9, 20, 0.1); padding: 1.5rem; border-radius: 8px; border: 1px solid rgba(229, 9, 20, 0.3); cursor: pointer; transition: all 0.3s ease;"
            onmouseover="this.style.transform='translateY(-5px)'; this.style.boxShadow='0 10px 25px rgba(229, 9, 20, 0.2)'"
            onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='none'"
          >
            <h3 style="color: #e50914; margin-bottom: 0.5rem; display: flex; align-items: center; gap: 0.5rem;">
              <i class="fas fa-theater-masks"></i> Salas
            </h3>
            <p style="color: #b3b3b3; font-size: 0.9rem;">Administrar salas de cine</p>
          </div>
          
          <div 
            style="background: rgba(229, 9, 20, 0.1); padding: 1.5rem; border-radius: 8px; border: 1px solid rgba(229, 9, 20, 0.3); cursor: pointer; transition: all 0.3s ease;"
            onmouseover="this.style.transform='translateY(-5px)'; this.style.boxShadow='0 10px 25px rgba(229, 9, 20, 0.2)'"
            onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='none'"
          >
            <h3 style="color: #e50914; margin-bottom: 0.5rem; display: flex; align-items: center; gap: 0.5rem;">
              <i class="fas fa-ticket-alt"></i> Tickets
            </h3>
            <p style="color: #b3b3b3; font-size: 0.9rem;">Sistema de venta de entradas</p>
          </div>
          
          <div 
            *ngIf="currentUser?.role === 'admin'"
            style="background: rgba(229, 9, 20, 0.1); padding: 1.5rem; border-radius: 8px; border: 1px solid rgba(229, 9, 20, 0.3); cursor: pointer; transition: all 0.3s ease;"
            onmouseover="this.style.transform='translateY(-5px)'; this.style.boxShadow='0 10px 25px rgba(229, 9, 20, 0.2)'"
            onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='none'"
          >
            <h3 style="color: #e50914; margin-bottom: 0.5rem; display: flex; align-items: center; gap: 0.5rem;">
              <i class="fas fa-users"></i> Usuarios
            </h3>
            <p style="color: #b3b3b3; font-size: 0.9rem;">Gestión de usuarios del sistema</p>
          </div>
        </div>
        
        <div style="margin-top: 2rem; padding: 1rem; background: rgba(70, 211, 105, 0.1); border: 1px solid rgba(70, 211, 105, 0.3); border-radius: 8px;">
          <p style="color: #46d369; margin: 0;">
            <i class="fas fa-check-circle"></i> <strong>Sistema funcionando correctamente</strong><br>
            Autenticación JWT activa. Tu sesión está protegida.
          </p>
        </div>

        <div *ngIf="currentUser?.role === 'admin'" style="margin-top: 1rem; padding: 1rem; background: rgba(255, 165, 0, 0.1); border: 1px solid rgba(255, 165, 0, 0.3); border-radius: 8px;">
          <p style="color: #ffa500; margin: 0;">
            <i class="fas fa-crown"></i> <strong>Privilegios de Administrador</strong><br>
            Tienes acceso completo al sistema y gestión de usuarios.
          </p>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .btn-logout:hover {
      background: #b8070f !important;
    }
  `]
})
export class DashboardComponent implements OnInit {
  currentUser: any = null;

  constructor(private router: Router) {}

  ngOnInit() {
    this.loadCurrentUser();
  }

  private loadCurrentUser() {
    const userData = localStorage.getItem('cinemax_user') || 
                    sessionStorage.getItem('cinemax_user');
    
    if (userData) {
      this.currentUser = JSON.parse(userData);
    }
  }

  logout() {
    // Limpiar tokens y datos del usuario
    localStorage.removeItem('cinemax_token');
    localStorage.removeItem('cinemax_user');
    sessionStorage.removeItem('cinemax_token');
    sessionStorage.removeItem('cinemax_user');
    
    // Redirigir al login
    this.router.navigate(['/login']);
  }
}