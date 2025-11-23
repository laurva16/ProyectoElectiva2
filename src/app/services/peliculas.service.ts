
// 1️⃣ peliculas.service.ts (CORREGIDO)
// ============================================
import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { API_CONFIG } from '../app.config';

@Injectable({
  providedIn: 'root'
})
export class PeliculasService {
  private apiUrl = `${API_CONFIG.BASE_URL}/peliculas`; // ✅ SIN /api duplicado

  constructor(private http: HttpClient) {}

  private getHeaders(): HttpHeaders {
    const token = localStorage.getItem('cinemax_token') || 
                  sessionStorage.getItem('cinemax_token');
    return new HttpHeaders({
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    });
  }

  obtenerPeliculas(): Observable<any> {
    return this.http.get(this.apiUrl, { headers: this.getHeaders() });
  }

  obtenerPeliculaPorId(id: number): Observable<any> {
    return this.http.get(`${this.apiUrl}/${id}`, { headers: this.getHeaders() });
  }

  crearPelicula(pelicula: any): Observable<any> {
    return this.http.post(this.apiUrl, pelicula, { headers: this.getHeaders() });
  }

  actualizarPelicula(id: number, pelicula: any): Observable<any> {
    return this.http.put(`${this.apiUrl}/${id}`, pelicula, { headers: this.getHeaders() });
  }

  eliminarPelicula(id: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/${id}`, { headers: this.getHeaders() });
  }
}