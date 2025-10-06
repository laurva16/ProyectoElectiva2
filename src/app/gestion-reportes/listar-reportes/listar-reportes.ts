import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Router } from '@angular/router';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-listar-reportes',
  standalone: true,
  imports: [CommonModule, RouterModule, FormsModule],
  templateUrl: './listar-reportes.html',
  styleUrl: './listar-reportes.css'
})
export class ListarReportes implements OnInit {
  loading = false;
  errorMessage = '';
  
  fechaInicio = '';
  fechaFin = '';
  
  reporteData: any = null;

  private apiUrl = 'http://localhost:5000/api/reportes';

  constructor(
    private http: HttpClient,
    private router: Router
  ) {}

  ngOnInit() {
    const today = new Date().toISOString().split('T')[0];
    this.fechaFin = today;
    
    const firstDayOfMonth = new Date();
    firstDayOfMonth.setDate(1);
    this.fechaInicio = firstDayOfMonth.toISOString().split('T')[0];
  }

  generarReporte() {
    this.loading = true;
    this.errorMessage = '';
    
    const token = this.getToken();
    const headers = new HttpHeaders({ 'Authorization': `Bearer ${token}` });
    
    let url = `${this.apiUrl}/ventas?`;
    if (this.fechaInicio) url += `fecha_inicio=${this.fechaInicio}&`;
    if (this.fechaFin) url += `fecha_fin=${this.fechaFin}`;

    this.http.get<any>(url, { headers }).subscribe({
      next: (response) => {
        this.loading = false;
        if (response.success) {
          this.reporteData = response.data;
        }
      },
      error: (error) => {
        this.loading = false;
        this.errorMessage = error.error?.message || 'Error al generar reporte';
      }
    });
  }

  descargarPDF() {
    this.loading = true;
    this.errorMessage = '';
    
    const token = this.getToken();
    const headers = new HttpHeaders({ 'Authorization': `Bearer ${token}` });
    
    let url = `${this.apiUrl}/ventas/pdf?`;
    if (this.fechaInicio) url += `fecha_inicio=${this.fechaInicio}&`;
    if (this.fechaFin) url += `fecha_fin=${this.fechaFin}`;

    this.http.get(url, { 
      headers, 
      responseType: 'blob' 
    }).subscribe({
      next: (blob) => {
        this.loading = false;
        
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `reporte_ventas_${new Date().getTime()}.pdf`;
        link.click();
        
        window.URL.revokeObjectURL(url);
      },
      error: (error) => {
        this.loading = false;
        this.errorMessage = 'Error al descargar PDF';
      }
    });
  }

  getToken(): string {
    return localStorage.getItem('cinemax_token') || sessionStorage.getItem('cinemax_token') || '';
  }

  volver() {
    this.router.navigate(['/dashboard']);
  }

  getVentasPeliculaArray(): any[] {
    if (!this.reporteData?.ventas_por_pelicula) return [];
    return Object.entries(this.reporteData.ventas_por_pelicula);
  }

  // ✅ AGREGAR ESTE MÉTODO
  getVentasSalaArray(): Array<{key: string, value: {cantidad: number, ingresos: number}}> {
    if (!this.reporteData?.ventas_por_sala) return [];
    return Object.entries(this.reporteData.ventas_por_sala).map(([key, value]: [string, any]) => ({
      key,
      value: value as {cantidad: number, ingresos: number}
    }));
  }
}