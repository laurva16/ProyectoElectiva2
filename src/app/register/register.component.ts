import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { HttpClient, HttpClientModule } from '@angular/common/http';

interface RegisterData {
  name: string;
  email: string;
  password: string;
  confirmPassword: string;
  role: string;
}

interface RegisterResponse {
  success: boolean;
  message: string;
  data?: any;
}

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [CommonModule, FormsModule, HttpClientModule, RouterModule],
  template: `
    <div class="register-container">
      <div class="register-card">
        <div class="register-header">
          <div class="logo-section">
            <i class="fas fa-user-plus"></i>
            <h1>Registrarse</h1>
            <p>Crear nueva cuenta en CineMax</p>
          </div>
        </div>
        
        <div class="register-form">
          <form (ngSubmit)="onRegister()" #registerForm="ngForm">
            <div class="form-group">
              <label for="name">
                <i class="fas fa-user"></i>
                Nombre Completo
              </label>
              <input 
                type="text" 
                id="name" 
                name="name" 
                [(ngModel)]="registerData.name"
                class="form-control"
                [ngClass]="{ 'error': nameError }"
                placeholder="Ingresa tu nombre completo"
                required
              >
              <div *ngIf="nameError" class="error-message">{{ nameError }}</div>
            </div>

            <div class="form-group">
              <label for="email">
                <i class="fas fa-envelope"></i>
                Correo Electrónico
              </label>
              <input 
                type="email" 
                id="email" 
                name="email" 
                [(ngModel)]="registerData.email"
                class="form-control"
                [ngClass]="{ 'error': emailError }"
                placeholder="tu@email.com"
                required
              >
              <div *ngIf="emailError" class="error-message">{{ emailError }}</div>
            </div>

            <div class="form-group">
              <label for="role">
                <i class="fas fa-briefcase"></i>
                Rol
              </label>
              <select 
                id="role" 
                name="role" 
                [(ngModel)]="registerData.role"
                class="form-control"
                required
              >
                <option value="employee">cliente</option>
                <option value="admin"></option>
              </select>
            </div>
            
            <div class="form-group">
              <label for="password">
                <i class="fas fa-lock"></i>
                Contraseña
              </label>
              <div class="password-input">
                <input 
                  [type]="showPassword ? 'text' : 'password'"
                  id="password"
                  name="password"
                  [(ngModel)]="registerData.password"
                  class="form-control"
                  [ngClass]="{ 'error': passwordError }"
                  placeholder="••••••••"
                  required
                >
                <button type="button" class="password-toggle" (click)="togglePasswordVisibility()">
                  <i [class]="showPassword ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
                </button>
              </div>
              <div *ngIf="passwordError" class="error-message">{{ passwordError }}</div>
            </div>

            <div class="form-group">
              <label for="confirmPassword">
                <i class="fas fa-lock"></i>
                Confirmar Contraseña
              </label>
              <input 
                [type]="showPassword ? 'text' : 'password'"
                id="confirmPassword"
                name="confirmPassword"
                [(ngModel)]="registerData.confirmPassword"
                class="form-control"
                [ngClass]="{ 'error': confirmPasswordError }"
                placeholder="••••••••"
                required
              >
              <div *ngIf="confirmPasswordError" class="error-message">{{ confirmPasswordError }}</div>
            </div>
            
            <button type="submit" class="btn btn-register" [disabled]="isLoading">
              <i class="fas fa-user-plus"></i>
              {{ isLoading ? 'Registrando...' : 'Crear Cuenta' }}
            </button>
          </form>

          <div *ngIf="alertMessage" [ngClass]="alertType === 'success' ? 'alert-success' : 'alert-error'" class="register-alert">
            <i [class]="getAlertIcon(alertType)"></i>
            <span>{{ alertMessage }}</span>
          </div>

          <div class="login-link">
            <p>¿Ya tienes cuenta? <a routerLink="/login">Iniciar Sesión</a></p>
          </div>
        </div>
      </div>
      
      <div class="loading-overlay" [ngClass]="{ 'active': isLoading }">
        <div class="loading-spinner">
          <i class="fas fa-spinner"></i>
          <p>Creando tu cuenta...</p>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .register-container {
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      background: linear-gradient(135deg, #141414 0%, #831010 50%, #141414 100%);
      padding: 2rem;
      position: relative;
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      color: #ffffff;
      line-height: 1.6;
    }

    .register-card {
      background: #1f1f1f;
      border-radius: 16px;
      box-shadow: 0 20px 40px rgba(0, 0, 0, 0.5);
      overflow: hidden;
      width: 100%;
      max-width: 500px;
      border: 1px solid #333333;
      position: relative;
      z-index: 1;
    }

    .register-header {
      background: linear-gradient(135deg, #e50914, #b8070f);
      padding: 2rem 2rem 1.5rem;
      text-align: center;
      color: white;
    }

    .logo-section i {
      font-size: 2.5rem;
      margin-bottom: 1rem;
      display: block;
    }

    .logo-section h1 {
      font-size: 2rem;
      font-weight: bold;
      margin-bottom: 0.5rem;
      text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
    }

    .logo-section p {
      opacity: 0.9;
      font-size: 0.9rem;
    }

    .register-form {
      padding: 2rem;
    }

    .form-group {
      margin-bottom: 1.5rem;
    }

    .form-group label {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      margin-bottom: 0.75rem;
      color: #ffffff;
      font-weight: 500;
    }

    .form-group label i {
      color: #e50914;
      width: 16px;
    }

    .form-control {
      width: 100%;
      padding: 1rem;
      background: #1f1f1f;
      border: 2px solid #333333;
      border-radius: 8px;
      color: #ffffff;
      font-size: 1rem;
      transition: all 0.3s ease;
    }

    .form-control::placeholder {
      color: #b3b3b3;
    }

    .form-control:focus {
      outline: none;
      border-color: #e50914;
      box-shadow: 0 0 0 3px rgba(229, 9, 20, 0.1);
      transform: translateY(-1px);
    }

    .form-control.error {
      border-color: #ff4757;
      box-shadow: 0 0 0 3px rgba(255, 71, 87, 0.1);
    }

    .password-input {
      position: relative;
    }

    .password-toggle {
      position: absolute;
      right: 12px;
      top: 50%;
      transform: translateY(-50%);
      background: none;
      border: none;
      color: #b3b3b3;
      cursor: pointer;
      padding: 0.25rem;
      transition: color 0.3s ease;
    }

    .password-toggle:hover {
      color: #e50914;
    }

    .btn-register {
      width: 100%;
      padding: 1rem;
      background: #e50914;
      color: white;
      border: none;
      border-radius: 8px;
      font-size: 1.1rem;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.3s ease;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 0.5rem;
    }

    .btn-register:hover:not(:disabled) {
      background: #b8070f;
      transform: translateY(-2px);
      box-shadow: 0 8px 25px rgba(229, 9, 20, 0.4);
    }

    .btn-register:disabled {
      opacity: 0.6;
      cursor: not-allowed;
    }

    .error-message {
      color: #ff4757;
      font-size: 0.85rem;
      margin-top: 0.5rem;
      display: flex;
      align-items: center;
      gap: 0.25rem;
    }

    .register-alert {
      padding: 1rem;
      border-radius: 8px;
      margin-bottom: 1rem;
      display: flex;
      align-items: center;
      gap: 0.75rem;
      animation: slideDown 0.3s ease;
    }

    .alert-success {
      background: rgba(70, 211, 105, 0.15);
      border: 1px solid rgba(70, 211, 105, 0.3);
      color: #46d369;
    }

    .alert-error {
      background: rgba(255, 71, 87, 0.15);
      border: 1px solid rgba(255, 71, 87, 0.3);
      color: #ff4757;
    }

    @keyframes slideDown {
      from {
        opacity: 0;
        transform: translateY(-10px);
      }
      to {
        opacity: 1;
        transform: translateY(0);
      }
    }

    .login-link {
      text-align: center;
      margin-top: 2rem;
      color: #b3b3b3;
    }

    .login-link a {
      color: #e50914;
      text-decoration: none;
      font-weight: 500;
    }

    .login-link a:hover {
      text-decoration: underline;
    }

    .loading-overlay {
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: rgba(0, 0, 0, 0.8);
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 1000;
      border-radius: 16px;
      opacity: 0;
      visibility: hidden;
      transition: all 0.3s ease;
    }

    .loading-overlay.active {
      opacity: 1;
      visibility: visible;
    }

    .loading-spinner {
      text-align: center;
      color: #ffffff;
    }

    .loading-spinner i {
      font-size: 2rem;
      color: #e50914;
      margin-bottom: 1rem;
      animation: spin 1s linear infinite;
    }

    @keyframes spin {
      0% { transform: rotate(0deg); }
      100% { transform: rotate(360deg); }
    }
  `]
})
export class RegisterComponent {
  registerData: RegisterData = {
    name: '',
    email: '',
    password: '',
    confirmPassword: '',
    role: 'employee'
  };

  isLoading = false;
  showPassword = false;
  alertMessage = '';
  alertType: 'success' | 'error' = 'success';
  
  // Errores de validación
  nameError = '';
  emailError = '';
  passwordError = '';
  confirmPasswordError = '';

  private apiUrl = 'http://localhost:5000/api';

  constructor(
    private router: Router,
    private http: HttpClient
  ) {}

  async onRegister() {
    if (!this.validateForm()) {
      return;
    }

    this.isLoading = true;
    this.clearErrors();

    try {
      const response = await this.http.post<RegisterResponse>(`${this.apiUrl}/auth/register`, {
        name: this.registerData.name,
        email: this.registerData.email,
        password: this.registerData.password,
        role: this.registerData.role
      }).toPromise();

      if (response?.success) {
        this.showAlert('¡Cuenta creada exitosamente! Redirigiendo al login...', 'success');
        setTimeout(() => {
          this.router.navigate(['/login']);
        }, 2000);
      } else {
        this.handleError(response?.message || 'Error al crear la cuenta');
      }
    } catch (error: any) {
      if (error.status === 409) {
        this.handleError('El usuario ya existe');
      } else if (error.status === 400) {
        this.handleError(error.error.message || 'Datos inválidos');
      } else {
        this.handleError('Error de conexión. Verifica que el servidor esté ejecutándose.');
      }
    } finally {
      this.isLoading = false;
    }
  }

  private validateForm(): boolean {
    let isValid = true;

    // Validar nombre
    if (!this.registerData.name.trim()) {
      this.nameError = 'El nombre es requerido';
      isValid = false;
    } else if (this.registerData.name.trim().length < 2) {
      this.nameError = 'El nombre debe tener al menos 2 caracteres';
      isValid = false;
    }

    // Validar email
    if (!this.registerData.email) {
      this.emailError = 'El email es requerido';
      isValid = false;
    } else if (!this.isValidEmail(this.registerData.email)) {
      this.emailError = 'Por favor ingresa un email válido';
      isValid = false;
    }

    // Validar password
    if (!this.registerData.password) {
      this.passwordError = 'La contraseña es requerida';
      isValid = false;
    } else if (this.registerData.password.length < 6) {
      this.passwordError = 'La contraseña debe tener al menos 6 caracteres';
      isValid = false;
    }

    // Validar confirmación de password
    if (!this.registerData.confirmPassword) {
      this.confirmPasswordError = 'Debes confirmar tu contraseña';
      isValid = false;
    } else if (this.registerData.password !== this.registerData.confirmPassword) {
      this.confirmPasswordError = 'Las contraseñas no coinciden';
      isValid = false;
    }

    return isValid;
  }

  private isValidEmail(email: string): boolean {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }

  private handleError(message: string) {
    this.showAlert(message, 'error');
  }

  private showAlert(message: string, type: 'success' | 'error') {
    this.alertMessage = message;
    this.alertType = type;

    setTimeout(() => {
      this.alertMessage = '';
    }, 5000);
  }

  private clearErrors() {
    this.nameError = '';
    this.emailError = '';
    this.passwordError = '';
    this.confirmPasswordError = '';
  }

  togglePasswordVisibility() {
    this.showPassword = !this.showPassword;
  }

  getAlertIcon(type: string): string {
    switch (type) {
      case 'success': return 'fas fa-check-circle';
      case 'error': return 'fas fa-exclamation-circle';
      default: return 'fas fa-info-circle';
    }
  }
}