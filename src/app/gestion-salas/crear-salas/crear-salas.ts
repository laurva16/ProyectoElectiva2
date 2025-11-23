import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule } from '@angular/router';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { SalasService } from '../../services/salas.service';

interface Sala {
  nombre: string;
  capacidad: number;
  tipo: string;
  tecnologia: string;
  estado: string;
  precio_base: number;
  filas: number;
  asientos_por_fila: number;
  descripcion?: string;
}

@Component({
  selector: 'app-crear-salas',
  standalone: true,
  imports: [CommonModule, RouterModule, ReactiveFormsModule],
  templateUrl: './crear-salas.html',
  styleUrl: './crear-salas.css'
})
export class CrearSalas implements OnInit {
  salaForm!: FormGroup;
  loading = false;
  errorMessage = '';
  successMessage = '';

  tipos = ['Estándar', 'VIP', 'IMAX', '4DX', 'Premium'];
  tecnologias = ['2D', '3D', 'IMAX', 'IMAX 3D', '4DX', 'Dolby Atmos'];
  estados = ['activa', 'mantenimiento', 'inactiva'];

  constructor(
    private fb: FormBuilder,
    private salasService: SalasService,
    private router: Router
  ) {}

  ngOnInit() {
    this.initForm();
  }

  initForm() {
    this.salaForm = this.fb.group({
      nombre: ['', [Validators.required, Validators.minLength(3), Validators.maxLength(100)]],
      capacidad: ['', [Validators.required, Validators.min(10), Validators.max(500)]],
      tipo: ['', Validators.required],
      tecnologia: ['', Validators.required],
      estado: ['activa', Validators.required],
      precio_base: ['', [Validators.required, Validators.min(0), Validators.max(999.99)]],
      filas: ['', [Validators.required, Validators.min(1), Validators.max(30)]],
      asientos_por_fila: ['', [Validators.required, Validators.min(5), Validators.max(50)]],
      descripcion: ['', [Validators.maxLength(500)]]
    });

    // Calcular capacidad automáticamente
    this.salaForm.get('filas')?.valueChanges.subscribe(() => this.calcularCapacidad());
    this.salaForm.get('asientos_por_fila')?.valueChanges.subscribe(() => this.calcularCapacidad());
  }

  calcularCapacidad() {
    const filas = this.salaForm.get('filas')?.value;
    const asientosPorFila = this.salaForm.get('asientos_por_fila')?.value;
    
    if (filas && asientosPorFila) {
      const capacidad = filas * asientosPorFila;
      this.salaForm.get('capacidad')?.setValue(capacidad, { emitEvent: false });
    }
  }

  onSubmit() {
    if (this.salaForm.invalid) {
      this.markFormGroupTouched(this.salaForm);
      this.errorMessage = 'Por favor completa todos los campos requeridos correctamente';
      return;
    }

    this.loading = true;
    this.errorMessage = '';
    this.successMessage = '';

    const salaData: Sala = this.salaForm.value;

    this.salasService.crearSala(salaData).subscribe({
      next: (response: any) => {
        this.loading = false;
        this.successMessage = 'Sala creada exitosamente';
        
        setTimeout(() => {
          this.router.navigate(['/salas/listar']);
        }, 1500);
      },
      error: (error) => {
        this.loading = false;
        console.error('Error al crear sala:', error);
        this.errorMessage = error.error?.message || 'Error al crear la sala. Intenta nuevamente.';
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
    const control = this.salaForm.get(fieldName);
    
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
    
    return '';
  }

  isFieldInvalid(fieldName: string): boolean {
    const control = this.salaForm.get(fieldName);
    return !!(control && control.invalid && (control.dirty || control.touched));
  }

  volver() {
    this.router.navigate(['/salas/listar']);
  }
}