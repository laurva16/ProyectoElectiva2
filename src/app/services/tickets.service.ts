import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { API_CONFIG } from '../app.config';

@Injectable({
  providedIn: 'root'
})
export class TicketsService {
  private apiUrl = `${API_CONFIG.BASE_URL}/tickets`; // ✅ SIN /api duplicado

  constructor(private http: HttpClient) {}

  private getHeaders(): HttpHeaders {
    const token = localStorage.getItem('cinemax_token') || 
                  sessionStorage.getItem('cinemax_token');
    return new HttpHeaders({
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    });
  }

  obtenerTickets(): Observable<any> {
    return this.http.get(this.apiUrl, { headers: this.getHeaders() });
  }

  obtenerTicketPorId(id: number): Observable<any> {
    return this.http.get(`${this.apiUrl}/${id}`, { headers: this.getHeaders() });
  }

  verificarDisponibilidad(salaId: number, fecha: string, hora: string): Observable<any> {
    const url = `${this.apiUrl}/disponibilidad?sala_id=${salaId}&fecha=${fecha}&hora=${hora}`;
    return this.http.get(url, { headers: this.getHeaders() });
  }

  crearTicket(ticket: any): Observable<any> {
    return this.http.post(this.apiUrl, ticket, { headers: this.getHeaders() });
  }

  eliminarTicket(id: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/${id}`, { headers: this.getHeaders() });
  }
}