import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { API_CONFIG } from '../app.config'; // ✅ Cambio de import

@Injectable({
  providedIn: 'root'
})
export class SalasService {
  private apiUrl = `${API_CONFIG.BASE_URL}/salas`; // ✅ Cambio de /app/salas a /salas

  constructor(private http: HttpClient) {}

  private getHeaders(): HttpHeaders {
    const token = localStorage.getItem('cinemax_token') || 
                  sessionStorage.getItem('cinemax_token');
    return new HttpHeaders({
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    });
  }

  obtenerSalas(): Observable<any> {
    return this.http.get(this.apiUrl, { headers: this.getHeaders() });
  }

  obtenerSalaPorId(id: number): Observable<any> {
    return this.http.get(`${this.apiUrl}/${id}`, { headers: this.getHeaders() });
  }

  crearSala(sala: any): Observable<any> {
    return this.http.post(this.apiUrl, sala, { headers: this.getHeaders() });
  }

  actualizarSala(id: number, sala: any): Observable<any> {
    return this.http.put(`${this.apiUrl}/${id}`, sala, { headers: this.getHeaders() });
  }

  eliminarSala(id: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/${id}`, { headers: this.getHeaders() });
  }
}