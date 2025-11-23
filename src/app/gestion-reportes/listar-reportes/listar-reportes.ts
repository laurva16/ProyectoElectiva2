import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Router } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { ReportesService } from '../../services/reportes.service';

interface VentaData {
  cantidad: number;
  ingresos: number;
}

interface ReporteData {
  resumen: {
    total_tickets: number;
    ingresos_totales: number;
    fecha_inicio: string;
    fecha_fin: string;
  };
  ventas_por_pelicula: { [key: string]: VentaData };
  ventas_por_sala: { [key: string]: VentaData };
}

interface ApiResponse {
  success: boolean;
  data: ReporteData;
  message?: string;
}

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
  
  reporteData: ReporteData | null = null;

  constructor(
    private reportesService: ReportesService,
    private router: Router
  ) {}

  ngOnInit() {
    // Inicializar fechas por defecto - TODO EL AÑO para capturar todos los tickets
    const today = new Date();
    this.fechaFin = this.formatDate(new Date(today.getFullYear(), 11, 31)); // 31 de diciembre
    
    const firstDayOfYear = new Date(today.getFullYear(), 0, 1); // 1 de enero
    this.fechaInicio = this.formatDate(firstDayOfYear);

    console.log('📅 Fechas inicializadas:', {
      inicio: this.fechaInicio,
      fin: this.fechaFin
    });
  }

  private formatDate(date: Date): string {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  }

  generarReporte() {
    console.log('📄 Generando reporte...');
    
    if (!this.fechaInicio || !this.fechaFin) {
      this.errorMessage = 'Por favor selecciona ambas fechas';
      return;
    }

    if (new Date(this.fechaInicio) > new Date(this.fechaFin)) {
      this.errorMessage = 'La fecha de inicio no puede ser mayor a la fecha fin';
      return;
    }

    this.loading = true;
    this.errorMessage = '';
    this.reporteData = null;
    
    console.log('🌐 Generando reporte con fechas:', this.fechaInicio, this.fechaFin);

    this.reportesService.generarReporteVentas(this.fechaInicio, this.fechaFin).subscribe({
      next: (response) => {
        console.log('✅ Respuesta del servidor:', response);
        this.loading = false;
        
        if (response.success && response.data) {
          this.reporteData = response.data;
          console.log('📊 Datos del reporte:', this.reporteData);
          
          // Debug adicional
          console.log('Películas:', this.getVentasPeliculaArray());
          console.log('Salas:', this.getVentasSalaArray());
        } else {
          this.errorMessage = response.message || 'No se pudo generar el reporte';
          console.error('❌ Error en respuesta:', response);
        }
      },
      error: (error) => {
        console.error('❌ Error HTTP:', error);
        this.loading = false;
        this.errorMessage = error.error?.message || error.message || 'Error al generar reporte';
      }
    });
  }

  descargarPDF() {
    console.log('📥 Descargando PDF...');
    
    if (!this.fechaInicio || !this.fechaFin) {
      this.errorMessage = 'Por favor selecciona ambas fechas';
      return;
    }

    this.loading = true;
    this.errorMessage = '';

    this.reportesService.descargarReportePDF(this.fechaInicio, this.fechaFin).subscribe({
      next: (blob) => {
        console.log('✅ PDF descargado');
        this.loading = false;
        
        const downloadUrl = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = downloadUrl;
        link.download = `reporte_ventas_${this.fechaInicio}_${this.fechaFin}.pdf`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        window.URL.revokeObjectURL(downloadUrl);
      },
      error: (error) => {
        console.error('❌ Error al descargar PDF:', error);
        this.loading = false;
        this.errorMessage = error.error?.message || 'Error al descargar PDF';
      }
    });
  }

  volver() {
    this.router.navigate(['/dashboard']);
  }

  getVentasPeliculaArray(): Array<[string, VentaData]> {
    if (!this.reporteData?.ventas_por_pelicula) {
      console.log('⚠️ No hay datos de ventas por película');
      return [];
    }
    return Object.entries(this.reporteData.ventas_por_pelicula);
  }

  getVentasSalaArray(): Array<{key: string, value: VentaData}> {
    if (!this.reporteData?.ventas_por_sala) {
      console.log('⚠️ No hay datos de ventas por sala');
      return [];
    }
    return Object.entries(this.reporteData.ventas_por_sala).map(([key, value]) => ({
      key,
      value
    }));
  }
}