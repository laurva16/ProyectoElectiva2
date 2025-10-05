import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule } from '@angular/router';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { HttpClient, HttpHeaders } from '@angular/common/http';

interface Pelicula {
  titulo: string;
  descripcion: string;
  duracion: number;
  genero: string;
  clasificacion: string;
  director?: string;
  actores?: string;
  imagen_url?: string;
  trailer_url?: string;
  fecha_estreno?: string;
  estado?: string;
  precio?: number;
}

@Component({
  selector: 'app-crear-peliculas',
  standalone: true,
  imports: [CommonModule, RouterModule, ReactiveFormsModule],
  templateUrl: './crear-peliculas.html',
  styleUrl: './crear-peliculas.css'
})
export class CrearPeliculas implements OnInit {
  peliculaForm!: FormGroup;
  loading = false;
  errorMessage = '';
  successMessage = '';

  generos = [
    'Acción',
    'Aventura',
    'Animación',
    'Ciencia Ficción',
    'Comedia',
    'Drama',
    'Fantasía',
    'Horror',
    'Romance',
    'Thriller',
    'Documental'
  ];

  clasificaciones = ['G', 'PG', 'PG-13', 'R', 'NC-17'];
  estados = ['disponible', 'cartelera', 'proximamente'];

  private apiUrl = 'http://localhost:5000/api/peliculas';

  constructor(
    private fb: FormBuilder,
    private http: HttpClient,
    private router: Router
  ) {}

  ngOnInit() {
    this.initForm();
  }

  initForm() {
    this.peliculaForm = this.fb.group({
      titulo: ['', [Validators.required, Validators.minLength(2), Validators.maxLength(200)]],
      descripcion: ['', [Validators.required, Validators.minLength(10), Validators.maxLength(1000)]],
      duracion: ['', [Validators.required, Validators.min(1), Validators.max(500)]],
      genero: ['', Validators.required],
      clasificacion: ['', Validators.required],
      director: ['', [Validators.maxLength(100)]],
      actores: ['', [Validators.maxLength(500)]],
      imagen_url: ['', [Validators.pattern(/^https?:\/\/.+/)]],
      trailer_url: ['', [Validators.pattern(/^https?:\/\/.+/)]],
      fecha_estreno: [''],
      estado: ['disponible', Validators.required],
      precio: ['', [Validators.min(0), Validators.max(999.99)]]
    });
  }

  // Método para abrir el trailer en una nueva pestaña
  abrirTrailer() {
    const trailerUrl = this.peliculaForm.get('trailer_url')?.value;
    if (trailerUrl && trailerUrl.trim() !== '') {
      window.open(trailerUrl, '_blank');
    }
  }

  onSubmit() {
    if (this.peliculaForm.invalid) {
      this.markFormGroupTouched(this.peliculaForm);
      this.errorMessage = 'Por favor completa todos los campos requeridos correctamente';
      return;
    }

    this.loading = true;
    this.errorMessage = '';
    this.successMessage = '';

    const token = localStorage.getItem('cinemax_token') || sessionStorage.getItem('cinemax_token');
    
    const headers = new HttpHeaders({
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    });

    const peliculaData: Pelicula = this.peliculaForm.value;

    this.http.post(this.apiUrl, peliculaData, { headers }).subscribe({
      next: (response: any) => {
        this.loading = false;
        this.successMessage = 'Película creada exitosamente';
        
        setTimeout(() => {
          this.router.navigate(['/peliculas/listar']);
        }, 1500);
      },
      error: (error) => {
        this.loading = false;
        console.error('Error al crear película:', error);
        this.errorMessage = error.error?.message || 'Error al crear la película. Intenta nuevamente.';
      }
    });
  }

  private markFormGroupTouched(formGroup: FormGroup) {
    Object.keys(formGroup.controls).forEach(key => {
      const control = formGroup.get(key);
      control?.markAsTouched();
    });
  }

  getFieldError(fieldName: string): string {
    const control = this.peliculaForm.get(fieldName);
    
    if (control?.hasError('required')) {
      return 'Este campo es requerido';
    }
    if (control?.hasError('minlength')) {
      const minLength = control.errors?.['minlength'].requiredLength;
      return `Mínimo ${minLength} caracteres`;
    }
    if (control?.hasError('maxlength')) {
      const maxLength = control.errors?.['maxlength'].requiredLength;
      return `Máximo ${maxLength} caracteres`;
    }
    if (control?.hasError('min')) {
      const min = control.errors?.['min'].min;
      return `Valor mínimo: ${min}`;
    }
    if (control?.hasError('max')) {
      const max = control.errors?.['max'].max;
      return `Valor máximo: ${max}`;
    }
    if (control?.hasError('pattern')) {
      return 'URL inválida (debe comenzar con http:// o https://)';
    }
    
    return '';
  }

  isFieldInvalid(fieldName: string): boolean {
    const control = this.peliculaForm.get(fieldName);
    return !!(control && control.invalid && (control.dirty || control.touched));
  }

  volver() {
    this.router.navigate(['/peliculas/listar']);
  }
}