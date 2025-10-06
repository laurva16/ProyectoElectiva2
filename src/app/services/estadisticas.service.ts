// src/app/services/estadisticas.service.ts
import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';

interface EstadisticasRapidas {
  total_peliculas: number;
  tickets_vendidos_hoy: number;
  total_salas: number;
  total_usuarios: number;
  ingresos_hoy: number;
}

@Injectable({
  providedIn: 'root'
})
export class EstadisticasService {
  private apiUrl = 'http://localhost:5000/api';

  constructor(private http: HttpClient) {}

  private getHeaders(): HttpHeaders {
    const token = localStorage.getItem('cinemax_token') || 
                  sessionStorage.getItem('cinemax_token');
    return new HttpHeaders({
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    });
  }

  obtenerEstadisticasRapidas(): Observable<any> {
    return this.http.get<any>(
      `${this.apiUrl}/reportes/estadisticas-rapidas`,
      { headers: this.getHeaders() }
    );
  }

  obtenerReporteVentas(fechaInicio?: string, fechaFin?: string): Observable<any> {
    let url = `${this.apiUrl}/reportes/ventas`;
    const params: string[] = [];
    
    if (fechaInicio) params.push(`fecha_inicio=${fechaInicio}`);
    if (fechaFin) params.push(`fecha_fin=${fechaFin}`);
    
    if (params.length > 0) {
      url += '?' + params.join('&');
    }
    
    return this.http.get<any>(url, { headers: this.getHeaders() });
  }
}