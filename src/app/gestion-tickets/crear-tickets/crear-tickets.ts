import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule } from '@angular/router';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { TicketsService } from '../../services/tickets.service';
import { PeliculasService } from '../../services/peliculas.service';
import { SalasService } from '../../services/salas.service';

interface Pelicula {
  id: number;
  titulo: string;
  precio: number;
}

interface Sala {
  id: number;
  nombre: string;
  precio_base: number;
  capacidad: number;
  filas: number;
  asientos_por_fila: number;
}

interface Asiento {
  nombre: string;
  fila: number;
  numero: number;
  disponible: boolean;
}

@Component({
  selector: 'app-crear-tickets',
  standalone: true,
  imports: [CommonModule, RouterModule, ReactiveFormsModule],
  templateUrl: './crear-tickets.html',
  styleUrl: './crear-tickets.css'
})
export class CrearTickets implements OnInit {
  ticketForm!: FormGroup;
  loading = false;
  errorMessage = '';
  successMessage = '';
  
  peliculas: Pelicula[] = [];
  salas: Sala[] = [];
  asientos: Asiento[] = [];
  asientoSeleccionado: Asiento | null = null;
  
  loadingAsientos = false;
  mostrarAsientos = false;

  constructor(
    private fb: FormBuilder,
    private ticketsService: TicketsService,
    private peliculasService: PeliculasService,
    private salasService: SalasService,
    private router: Router
  ) {}

  ngOnInit() {
    this.initForm();
    this.cargarPeliculas();
    this.cargarSalas();
  }

  initForm() {
    const today = new Date().toISOString().split('T')[0];
    
    this.ticketForm = this.fb.group({
      pelicula_id: ['', Validators.required],
      sala_id: ['', Validators.required],
      fecha_funcion: [today, Validators.required],
      hora_funcion: ['', Validators.required],
      asiento: ['', Validators.required],
      precio: ['', [Validators.required, Validators.min(0)]],
      metodo_pago: ['efectivo', Validators.required],
      estado: ['reservado', Validators.required]
    });

    // Auto-calcular precio cuando cambie película o sala
    this.ticketForm.get('pelicula_id')?.valueChanges.subscribe(() => this.calcularPrecio());
    this.ticketForm.get('sala_id')?.valueChanges.subscribe(() => this.calcularPrecio());
  }

  cargarPeliculas() {
    this.peliculasService.obtenerPeliculas().subscribe({
      next: (response) => {
        if (response.success) {
          // Debug: Ver todas las películas y sus estados
          console.log('🎬 Total de películas recibidas:', response.data.length);
          console.log('Estados encontrados:', response.data.map((p: any) => `${p.titulo}: ${p.estado}`));
          
          // Filtrar películas disponibles para venta (cartelera y disponible)
          this.peliculas = response.data.filter((p: any) => {
            const estado = p.estado?.toLowerCase().trim();
            return estado === 'cartelera' || estado === 'disponible';
          });
          
          console.log('✅ Películas disponibles para tickets:', this.peliculas.length);
          
          // Advertencia si no hay películas disponibles
          if (this.peliculas.length === 0) {
            console.warn('⚠️ No hay películas disponibles. Verifica los estados en la BD.');
            this.errorMessage = 'No hay películas disponibles para crear tickets';
          }
        }
      },
      error: (error) => {
        console.error('Error al cargar películas:', error);
        this.errorMessage = 'Error al cargar las películas';
      }
    });
  }

  cargarSalas() {
    this.salasService.obtenerSalas().subscribe({
      next: (response) => {
        if (response.success) {
          this.salas = response.data.filter((s: any) => s.estado === 'activa');
        }
      },
      error: (error) => console.error('Error al cargar salas:', error)
    });
  }

  calcularPrecio() {
    const peliculaId = this.ticketForm.get('pelicula_id')?.value;
    const salaId = this.ticketForm.get('sala_id')?.value;

    if (peliculaId && salaId) {
      const pelicula = this.peliculas.find(p => p.id == peliculaId);
      const sala = this.salas.find(s => s.id == salaId);

      if (pelicula && sala) {
        const precio = (pelicula.precio || 0) + (sala.precio_base || 0);
        this.ticketForm.get('precio')?.setValue(precio.toFixed(2));
      }
    }
  }

  verificarDisponibilidad() {
    const salaId = this.ticketForm.get('sala_id')?.value;
    const fecha = this.ticketForm.get('fecha_funcion')?.value;
    const hora = this.ticketForm.get('hora_funcion')?.value;

    if (!salaId || !fecha || !hora) {
      this.errorMessage = 'Por favor selecciona sala, fecha y hora';
      return;
    }

    this.loadingAsientos = true;
    this.errorMessage = '';

    this.ticketsService.verificarDisponibilidad(salaId, fecha, hora).subscribe({
      next: (response) => {
        this.loadingAsientos = false;
        if (response.success) {
          this.asientos = response.data.asientos;
          this.mostrarAsientos = true;
        }
      },
      error: (error) => {
        this.loadingAsientos = false;
        this.errorMessage = error.error?.message || 'Error al cargar disponibilidad';
      }
    });
  }

  seleccionarAsiento(asiento: Asiento) {
    if (!asiento.disponible) return;

    this.asientoSeleccionado = asiento;
    this.ticketForm.get('asiento')?.setValue(asiento.nombre);
  }

  onSubmit() {
    if (this.ticketForm.invalid) {
      this.markFormGroupTouched(this.ticketForm);
      this.errorMessage = 'Por favor completa todos los campos requeridos';
      return;
    }

    this.loading = true;
    this.errorMessage = '';
    this.successMessage = '';

    this.ticketsService.crearTicket(this.ticketForm.value).subscribe({
      next: (response: any) => {
        this.loading = false;
        this.successMessage = 'Ticket creado exitosamente';
        
        setTimeout(() => {
          this.router.navigate(['/tickets/listar']);
        }, 1500);
      },
      error: (error) => {
        this.loading = false;
        console.error('Error al crear ticket:', error);
        this.errorMessage = error.error?.message || 'Error al crear el ticket';
      }
    });
  }

  private markFormGroupTouched(formGroup: FormGroup) {
    Object.keys(formGroup.controls).forEach(key => {
      formGroup.get(key)?.markAsTouched();
    });
  }

  getFieldError(fieldName: string): string {
    const control = this.ticketForm.get(fieldName);
    
    if (control?.hasError('required')) return 'Este campo es requerido';
    if (control?.hasError('min')) return `Valor mínimo: ${control.errors?.['min'].min}`;
    
    return '';
  }

  isFieldInvalid(fieldName: string): boolean {
    const control = this.ticketForm.get(fieldName);
    return !!(control && control.invalid && (control.dirty || control.touched));
  }

  volver() {
    this.router.navigate(['/tickets/listar']);
  }
}