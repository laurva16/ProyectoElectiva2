import { Injectable } from '@angular/core';
import { CanActivate, Router, ActivatedRouteSnapshot, RouterStateSnapshot } from '@angular/router';
import { HttpClient } from '@angular/common/http';

@Injectable({
  providedIn: 'root'
})
export class AuthGuard implements CanActivate {
  private apiUrl = 'http://localhost:5000/api';

  constructor(
    private router: Router,
    private http: HttpClient
  ) {}

  async canActivate(
    route: ActivatedRouteSnapshot,
    state: RouterStateSnapshot
  ): Promise<boolean> {
    const token = this.getToken();
    
    if (!token) {
      this.redirectToLogin();
      return false;
    }

    // Verificar si el token es válido
    const isValid = await this.verifyToken(token);
    
    if (!isValid) {
      this.clearTokens();
      this.redirectToLogin();
      return false;
    }

    return true;
  }

  private getToken(): string | null {
    return localStorage.getItem('cinemax_token') || 
           sessionStorage.getItem('cinemax_token');
  }

  private async verifyToken(token: string): Promise<boolean> {
    try {
      const response = await this.http.get(`${this.apiUrl}/auth/verify`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      }).toPromise();

      return response && (response as any).success;
    } catch (error) {
      console.error('Token verification failed:', error);
      return false;
    }
  }

  private clearTokens(): void {
    localStorage.removeItem('cinemax_token');
    localStorage.removeItem('cinemax_user');
    sessionStorage.removeItem('cinemax_token');
    sessionStorage.removeItem('cinemax_user');
  }

  private redirectToLogin(): void {
    this.router.navigate(['/login']);
  }
}