import { Component, OnInit, ViewEncapsulation } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router,RouterModule  } from '@angular/router';
import { HttpClient, HttpClientModule } from '@angular/common/http';

interface LoginCredentials {
  email: string;
  password: string;
  rememberMe: boolean;
}

interface LoginResponse {
  success: boolean;
  message: string;
  data?: {
    user: {
      name: string;
      email: string;
      role: string;
      permissions: string[];
    };
    access_token: string;
  };
}

interface ConnectionStatus {
  isOnline: boolean;
  message: string;
}

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, FormsModule, HttpClientModule, RouterModule],
  templateUrl: './login.html',
  styleUrls: ['./login.css'],
  encapsulation: ViewEncapsulation.None  // Esto hace que los estilos se apliquen globalmente
})
export class Login implements OnInit {
  // Propiedades del componente
  credentials: LoginCredentials = {
    email: '',
    password: '',
    rememberMe: false
  };

  // Estados del componente
  isLoading = false;
  showPassword = false;
  alertMessage = '';
  alertType: 'success' | 'error' | 'warning' = 'success';
  
  // Errores de validación
  emailError = '';
  passwordError = '';

  // Estado de conexión
  connectionStatus: ConnectionStatus = {
    isOnline: false,
    message: 'Verificando conexión...'
  };

  // Configuración de API
  private apiUrl = 'http://localhost:5000/api';

  constructor(
    private router: Router,
    private http: HttpClient
  ) {}

  ngOnInit() {
    this.checkConnection();
    this.checkStoredSession();
  }

  async onLogin() {
    if (!this.validateForm()) {
      return;
    }

    this.isLoading = true;
    this.clearErrors();

    try {
      // Simulación de llamada a API (reemplaza con tu servicio real)
      const response = await this.authenticateUser(this.credentials);
      
      if (response.success && response.data) {
        this.handleSuccessfulLogin(response.data, this.credentials.rememberMe);
      } else {
        this.handleFailedLogin(response.message || 'Error de autenticación');
      }
    } catch (error) {
      this.handleFailedLogin('Error de conexión. Verifica que el servidor esté ejecutándose.');
    } finally {
      this.isLoading = false;
    }
  }

  private async authenticateUser(credentials: LoginCredentials): Promise<LoginResponse> {
  console.log('Enviando credenciales:', {
    email: credentials.email,
    password: credentials.password ? '***' : 'VACÍO'
  });

  try {
    const response = await this.http.post<any>(`${this.apiUrl}/auth/login`, {
      email: credentials.email,
      password: credentials.password,
      rememberMe: credentials.rememberMe
    }).toPromise();

    console.log('Login exitoso:', response);
    return response as LoginResponse;
  } catch (error: any) {
    console.log('Error completo:', error);
    console.log('Status:', error.status);
    console.log('Mensaje del servidor:', error.error);
    
    if (error.status === 401) {
      return {
        success: false,
        message: error.error?.message || 'Credenciales incorrectas'
      };
    } else if (error.status === 400) {
      return {
        success: false,
        message: error.error?.message || 'Datos incompletos'
      };
    } else {
      throw error;
    }
  }
}
  private validateForm(): boolean {
    let isValid = true;

    // Validar email
    if (!this.credentials.email) {
      this.emailError = 'El email es requerido';
      isValid = false;
    } else if (!this.isValidEmail(this.credentials.email)) {
      this.emailError = 'Por favor ingresa un email válido';
      isValid = false;
    }

    // Validar password
    if (!this.credentials.password) {
      this.passwordError = 'La contraseña es requerida';
      isValid = false;
    } else if (this.credentials.password.length < 3) {
      this.passwordError = 'La contraseña debe tener al menos 3 caracteres';
      isValid = false;
    }

    return isValid;
  }

  private isValidEmail(email: string): boolean {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }

  private handleSuccessfulLogin(data: any, rememberMe: boolean) {
    const { user, access_token } = data;

    // Almacenar token
    const storage = rememberMe ? localStorage : sessionStorage;
    storage.setItem('cinemax_token', access_token);
    storage.setItem('cinemax_user', JSON.stringify(user));

    this.showAlert(`¡Bienvenido ${user.name}!`, 'success');

    // Redirigir al dashboard después de 1.5 segundos
    setTimeout(() => {
      this.router.navigate(['/dashboard']); // Cambiado a dashboard
    }, 1500);
  }

  private handleFailedLogin(message: string) {
    this.showAlert(message, 'error');
  }

  private showAlert(message: string, type: 'success' | 'error' | 'warning') {
    this.alertMessage = message;
    this.alertType = type;

    // Limpiar alerta después de 5 segundos
    setTimeout(() => {
      this.alertMessage = '';
    }, 5000);
  }

  private clearErrors() {
    this.emailError = '';
    this.passwordError = '';
  }

  // Métodos públicos para el template
  togglePasswordVisibility() {
    this.showPassword = !this.showPassword;
  }

  fillCredentials(email: string, password: string) {
    this.credentials.email = email;
    this.credentials.password = password;
  }

  getAlertIcon(type: string): string {
    switch (type) {
      case 'success': return 'fas fa-check-circle';
      case 'error': return 'fas fa-exclamation-circle';
      case 'warning': return 'fas fa-exclamation-triangle';
      default: return 'fas fa-info-circle';
    }
  }

  private async checkConnection() {
    try {
      // Verificar conexión con tu servidor Flask
      const response = await this.http.get(`${this.apiUrl.replace('/api', '')}`).toPromise();
      this.connectionStatus = {
        isOnline: true,
        message: 'Conectado'
      };
    } catch (error) {
      this.connectionStatus = {
        isOnline: false,
        message: 'Sin conexión'
      };
    }
  }

  private checkStoredSession() {
    const token = localStorage.getItem('cinemax_token') || sessionStorage.getItem('cinemax_token');
    
    if (token) {
      const userData = JSON.parse(
        localStorage.getItem('cinemax_user') || 
        sessionStorage.getItem('cinemax_user') || 
        '{}'
      );
      
      if (userData.name) {
        this.showAlert('Sesión activa encontrada', 'success');
        setTimeout(() => {
          this.router.navigate(['/dashboard']); 
        }, 1000);
      }
    }
  }
}