import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule } from '@angular/router';
import { HttpClient } from '@angular/common/http';

interface Pelicula {
  id?: number;
  titulo: string;
  descripcion: string;
  duracion: number;
  genero: string;
  clasificacion: string;
  imagen_url?: string;
  estado: string;
}

@Component({
  selector: 'app-listar-peliculas',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './listar-peliculas.html',
  styleUrl: './listar-peliculas.css'
})
export class ListarPeliculas implements OnInit {
  peliculas: Pelicula[] = [];
  peliculasFiltradas: Pelicula[] = [];
  loading = false;
  searchTerm = '';
  filtroGenero = '';
  generos: string[] = [];

  // URL de tu backend - AJÚSTALA según tu configuración
  private apiUrl = 'http://localhost:5000/api/peliculas';

  constructor(
    private http: HttpClient,
    private router: Router
  ) {}

  ngOnInit() {
    this.cargarPeliculas();
  }

  cargarPeliculas() {
    this.loading = true;
    // Por ahora datos de ejemplo - conectarás con tu backend
    setTimeout(() => {
      this.peliculas = [
        {
          id: 1,
          titulo: 'Spider-Man: Across the Spider-Verse',
          descripcion: 'Miles Morales catapulta a través del Multiverso',
          duracion: 140,
          genero: 'Animación',
          clasificacion: 'PG-13',
          imagen_url: 'https://image.tmdb.org/t/p/w500/gh4cZbhZxyTbgxQPxD0dOudNPTn.jpg',
          estado: 'cartelera'
        },
        {
          id: 2,
          titulo: 'The Flash',
          descripcion: 'Barry Allen usa sus superpoderes para viajar en el tiempo',
          duracion: 144,
          genero: 'Acción',
          clasificacion: 'PG-13',
          imagen_url: 'https://image.tmdb.org/t/p/w500/rktDFPbfHfUbArZ6OOOKsXcv0Bm.jpg',
          estado: 'cartelera'
        },
        {
          id: 3,
          titulo: 'Elemental',
          descripcion: 'En una ciudad donde los elementos viven juntos',
          duracion: 109,
          genero: 'Animación',
          clasificacion: 'PG',
          imagen_url: 'https://image.tmdb.org/t/p/w500/6oH378KUfCEitzJkm07r97L0RsZ.jpg',
          estado: 'cartelera'
        },
        {
          id: 4,
          titulo: 'Interstellar',
          descripcion: 'Un grupo de exploradores viaja a través de un agujero de gusano',
          duracion: 169,
          genero: 'Ciencia Ficción',
          clasificacion: 'PG-13',
          imagen_url: 'https://image.tmdb.org/t/p/w500/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg',
          estado: 'disponible'
        }
      ];
      
      this.peliculasFiltradas = [...this.peliculas];
      this.extraerGeneros();
      this.loading = false;
    }, 500);

    // Cuando conectes con tu backend, usa esto:
    /*
    this.http.get<Pelicula[]>(this.apiUrl).subscribe({
      next: (data) => {
        this.peliculas = data;
        this.peliculasFiltradas = [...this.peliculas];
        this.extraerGeneros();
        this.loading = false;
      },
      error: (error) => {
        console.error('Error al cargar películas:', error);
        this.loading = false;
      }
    });
    */
  }

  extraerGeneros() {
    const generosUnicos = new Set(this.peliculas.map(p => p.genero));
    this.generos = Array.from(generosUnicos);
  }

  buscar(event: Event) {
    const target = event.target as HTMLInputElement;
    this.searchTerm = target.value.toLowerCase();
    this.filtrarPeliculas();
  }

  filtrarPorGenero(event: Event) {
    const target = event.target as HTMLSelectElement;
    this.filtroGenero = target.value;
    this.filtrarPeliculas();
  }

  filtrarPeliculas() {
    this.peliculasFiltradas = this.peliculas.filter(pelicula => {
      const coincideBusqueda = this.searchTerm === '' || 
        pelicula.titulo.toLowerCase().includes(this.searchTerm) ||
        pelicula.descripcion.toLowerCase().includes(this.searchTerm);
      
      const coincideGenero = this.filtroGenero === '' || 
        pelicula.genero === this.filtroGenero;
      
      return coincideBusqueda && coincideGenero;
    });
  }

  verDetalle(id: number) {
    // Navegar a detalle de película
    console.log('Ver detalle de película:', id);
  }

  editarPelicula(id: number) {
    // Navegar a editar película
    this.router.navigate(['/peliculas/editar', id]);
  }

  eliminarPelicula(id: number) {
    if (confirm('¿Estás seguro de eliminar esta película?')) {
      // Llamar al backend para eliminar
      console.log('Eliminar película:', id);
      this.peliculas = this.peliculas.filter(p => p.id !== id);
      this.filtrarPeliculas();
    }
  }

  crearNuevaPelicula() {
    this.router.navigate(['/peliculas/crear']);
  }

  volverDashboard() {
    this.router.navigate(['/dashboard']);
  }
}