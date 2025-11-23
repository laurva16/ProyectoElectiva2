import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { TicketsService } from '../../services/tickets.service';

interface Ticket {
  id: number;
  pelicula_id: number;
  pelicula_nombre: string;
  sala_id: number;
  sala_nombre: string;
  usuario_id: number;
  usuario_nombre: string;
  asiento: string;
  fecha_funcion: string;
  hora_funcion: string;
  precio: number;
  estado: string;
  metodo_pago: string;
  codigo_qr: string;
  created_at?: string;
}

@Component({
  selector: 'app-listar-tickets',
  standalone: true,
  imports: [CommonModule, RouterModule, FormsModule],
  templateUrl: './listar-tickets.html',
  styleUrl: './listar-tickets.css'
})
export class ListarTickets implements OnInit {
  tickets: Ticket[] = [];
  ticketsFiltrados: Ticket[] = [];
  loading = true;
  
  // Filtros
  searchTerm = '';
  filtroEstado = '';
  filtroFecha = '';
  
  // Modal
  showModal = false;
  ticketSeleccionado: Ticket | null = null;

  constructor(
    private ticketsService: TicketsService,
    private router: Router
  ) {}

  ngOnInit() {
    // Inicializar el filtro de fecha con el mes actual
    this.inicializarFiltroFecha();
    this.cargarTickets();
  }

  private inicializarFiltroFecha() {
    // Establecer filtro de fecha para el mes actual por defecto
    const hoy = new Date();
    // Formato: YYYY-MM para el input type="month"
    const año = hoy.getFullYear();
    const mes = String(hoy.getMonth() + 1).padStart(2, '0');
    
    // Si tu HTML usa input type="date", usa esto:
    // this.filtroFecha = `${año}-${mes}-${String(hoy.getDate()).padStart(2, '0')}`;
    
    // Si tu HTML usa input type="month", usa esto:
    // this.filtroFecha = `${año}-${mes}`;
    
    // Por ahora, lo dejamos vacío para mostrar todos los tickets
    console.log('📅 Filtro de fecha inicializado para:', `${año}-${mes}`);
  }

  cargarTickets() {
    this.loading = true;

    this.ticketsService.obtenerTickets().subscribe({
      next: (response) => {
        this.loading = false;
        if (response.success) {
          this.tickets = response.data;
          console.log(`✅ ${this.tickets.length} tickets cargados`);
          this.aplicarFiltros();
        }
      },
      error: (error) => {
        this.loading = false;
        console.error('❌ Error al cargar tickets:', error);
        
        if (error.status === 401) {
          this.router.navigate(['/login']);
        }
      }
    });
  }

  aplicarFiltros() {
    this.ticketsFiltrados = this.tickets.filter(ticket => {
      const cumpleBusqueda = 
        ticket.pelicula_nombre.toLowerCase().includes(this.searchTerm.toLowerCase()) ||
        ticket.sala_nombre.toLowerCase().includes(this.searchTerm.toLowerCase()) ||
        ticket.usuario_nombre.toLowerCase().includes(this.searchTerm.toLowerCase()) ||
        ticket.asiento.toLowerCase().includes(this.searchTerm.toLowerCase());
      
      const cumpleEstado = !this.filtroEstado || ticket.estado === this.filtroEstado;
      const cumpleFecha = !this.filtroFecha || ticket.fecha_funcion === this.filtroFecha;
      
      return cumpleBusqueda && cumpleEstado && cumpleFecha;
    });
    
    console.log(`🔍 Filtros aplicados: ${this.ticketsFiltrados.length} tickets mostrados`);
  }

  onSearchChange() {
    this.aplicarFiltros();
  }

  onFiltroEstadoChange() {
    this.aplicarFiltros();
  }

  onFiltroFechaChange() {
    this.aplicarFiltros();
  }

  limpiarFiltros() {
    this.searchTerm = '';
    this.filtroEstado = '';
    this.filtroFecha = '';
    this.aplicarFiltros();
  }

  verDetalle(ticket: Ticket) {
    this.ticketSeleccionado = ticket;
    this.showModal = true;
  }

  cerrarModal() {
    this.showModal = false;
    this.ticketSeleccionado = null;
  }

  cancelarTicket(ticket: Ticket) {
    if (!confirm(`¿Estás seguro de cancelar el ticket #${ticket.id}?`)) {
      return;
    }

    this.ticketsService.eliminarTicket(ticket.id).subscribe({
      next: (response: any) => {
        if (response.success) {
          // Actualizar estado localmente
          const index = this.tickets.findIndex(t => t.id === ticket.id);
          if (index !== -1) {
            this.tickets[index].estado = 'cancelado';
          }
          this.aplicarFiltros();
          alert('Ticket cancelado exitosamente');
        }
      },
      error: (error) => {
        console.error('Error al cancelar ticket:', error);
        alert(error.error?.message || 'Error al cancelar el ticket');
      }
    });
  }

  imprimirTicket(ticket: Ticket) {
    // Aquí podrías implementar la lógica de impresión
    alert(`Imprimir ticket #${ticket.id}\nCódigo QR: ${ticket.codigo_qr}`);
  }

  crearNuevoTicket() {
    this.router.navigate(['/tickets/crear']);
  }

  volver() {
    this.router.navigate(['/dashboard']);
  }

  getEstadoClass(estado: string): string {
    const clases: { [key: string]: string } = {
      'reservado': 'estado-reservado',
      'pagado': 'estado-pagado',
      'cancelado': 'estado-cancelado',
      'usado': 'estado-usado'
    };
    return clases[estado] || '';
  }

  getEstadoIcon(estado: string): string {
    const iconos: { [key: string]: string } = {
      'reservado': 'fa-clock',
      'pagado': 'fa-check-circle',
      'cancelado': 'fa-times-circle',
      'usado': 'fa-check-double'
    };
    return iconos[estado] || 'fa-ticket-alt';
  }
}