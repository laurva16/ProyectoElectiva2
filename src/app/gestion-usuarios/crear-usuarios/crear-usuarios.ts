import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule } from '@angular/router';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { HttpClient, HttpHeaders } from '@angular/common/http';

interface Usuario {
  email: string;
  password: string;
  name: string;
  role: string;
  telefono?: string;
  direccion?: string;
}

@Component({
  selector: 'app-crear-usuarios',
  standalone: true,
  imports: [CommonModule, RouterModule, ReactiveFormsModule],
  templateUrl: './crear-usuarios.html',
  styleUrl: './crear-usuarios.css'
})
export class CrearUsuarios implements OnInit {
  usuarioForm!: FormGroup;
  loading = false;
  errorMessage = '';
  successMessage = '';

  roles = [
    { value: 'cliente', label: 'Cliente' },
    { value: 'cajero', label: 'Cajero' },
    { value: 'admin', label: 'Administrador' }
  ];

  private apiUrl = 'http://localhost:5000/api/usuarios';

  constructor(
    private fb: FormBuilder,
    private http: HttpClient,
    private router: Router
  ) {}

  ngOnInit() {
    this.initForm();
  }

  initForm() {
    this.usuarioForm = this.fb.group({
      name: ['', [Validators.required, Validators.minLength(3), Validators.maxLength(100)]],
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required, Validators.minLength(6), Validators.maxLength(50)]],
      confirmPassword: ['', [Validators.required]],
      role: ['cliente', Validators.required],
      telefono: ['', [Validators.pattern(/^\+?\d{10,15}$/)]],
      direccion: ['', [Validators.maxLength(200)]]
    }, {
      validators: this.passwordMatchValidator
    });
  }

  passwordMatchValidator(form: FormGroup) {
    const password = form.get('password');
    const confirmPassword = form.get('confirmPassword');
    
    if (password && confirmPassword && password.value !== confirmPassword.value) {
      confirmPassword.setErrors({ passwordMismatch: true });
      return { passwordMismatch: true };
    }
    return null;
  }

  onSubmit() {
    if (this.usuarioForm.invalid) {
      this.markFormGroupTouched(this.usuarioForm);
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

    const { confirmPassword, ...usuarioData } = this.usuarioForm.value;

    this.http.post(this.apiUrl, usuarioData, { headers }).subscribe({
      next: (response: any) => {
        this.loading = false;
        this.successMessage = 'Usuario creado exitosamente';
        
        setTimeout(() => {
          this.router.navigate(['/usuarios/listar']);
        }, 1500);
      },
      error: (error) => {
        this.loading = false;
        console.error('Error al crear usuario:', error);
        this.errorMessage = error.error?.message || 'Error al crear el usuario. Intenta nuevamente.';
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
    const control = this.usuarioForm.get(fieldName);
    
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
    if (control?.hasError('email')) {
      return 'Email inválido';
    }
    if (control?.hasError('pattern')) {
      if (fieldName === 'telefono') {
        return 'Formato de teléfono inválido (ej: +573001234567)';
      }
      return 'Formato inválido';
    }
    if (control?.hasError('passwordMismatch')) {
      return 'Las contraseñas no coinciden';
    }
    
    return '';
  }

  isFieldInvalid(fieldName: string): boolean {
    const control = this.usuarioForm.get(fieldName);
    return !!(control && control.invalid && (control.dirty || control.touched));
  }

  volver() {
    this.router.navigate(['/usuarios/listar']);
  }
}