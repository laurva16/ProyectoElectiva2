import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { API_CONFIG } from '../app.config';

@Injectable({
  providedIn: 'root'
})
export class ReportesService {
  private apiUrl = `${API_CONFIG.BASE_URL}/reportes`; // ✅ SIN /api duplicado

  constructor(private http: HttpClient) {}

  private getHeaders(): HttpHeaders {
    const token = localStorage.getItem('cinemax_token') || 
                  sessionStorage.getItem('cinemax_token');
    return new HttpHeaders({
      'Authorization': `Bearer ${token}`
    });
  }

  generarReporteVentas(fechaInicio: string, fechaFin: string): Observable<any> {
    const url = `${this.apiUrl}/ventas?fecha_inicio=${fechaInicio}&fecha_fin=${fechaFin}`;
    return this.http.get(url, { headers: this.getHeaders() });
  }

  descargarReportePDF(fechaInicio: string, fechaFin: string): Observable<Blob> {
    const url = `${this.apiUrl}/ventas/pdf?fecha_inicio=${fechaInicio}&fecha_fin=${fechaFin}`;
    return this.http.get(url, { 
      headers: this.getHeaders(),
      responseType: 'blob'
    });
  }
}
