import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule } from '@angular/router';
import { HttpClient, HttpHeaders } from '@angular/common/http';

interface Pelicula {
  id?: number;
  titulo: string;
  descripcion: string;
  duracion: number;
  genero: string;
  clasificacion: string;
  imagen_url?: string;
  trailer_url?: string;
  estado: string;
  director?: string;
  actores?: string;
  fecha_estreno?: string;
  precio?: number;
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
  peliculaSeleccionada: Pelicula | null = null;
  
  // Usuario actual
  currentUser: any = null;

  // Getter para verificar si es admin
  get isAdmin(): boolean {
    return this.currentUser?.role === 'admin';
  }

  private apiUrl = 'http://localhost:5000/api/peliculas';

  constructor(
    private http: HttpClient,
    private router: Router
  ) {}

  ngOnInit() {
    this.loadCurrentUser();
    this.cargarPeliculas();
  }

  private loadCurrentUser() {
    const userData = localStorage.getItem('cinemax_user') || 
                    sessionStorage.getItem('cinemax_user');
    
    if (userData) {
      this.currentUser = JSON.parse(userData);
    }
  }

  cargarPeliculas() {
    this.loading = true;
    
    const token = localStorage.getItem('cinemax_token') || 
                  sessionStorage.getItem('cinemax_token');
    
    const headers = new HttpHeaders({
      'Authorization': `Bearer ${token}`
    });

    this.http.get<any>(this.apiUrl, { headers }).subscribe({
      next: (response) => {
        const peliculasBackend = response.data || [];
        
        const peliculasEstaticas = [
          {
            id: 1,
            titulo: 'Spider-Man: Across the Spider-Verse',
            descripcion: 'Miles Morales catapulta a través del Multiverso',
            duracion: 140,
            genero: 'Animación',
            clasificacion: 'PG-13',
            imagen_url: 'https://image.tmdb.org/t/p/w500/gh4cZbhZxyTbgxQPxD0dOudNPTn.jpg',
            trailer_url: 'https://www.youtube.com/watch?v=cqGjhVJWtEg',
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
            trailer_url: 'https://www.youtube.com/watch?v=hebWYacbdvc',
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
            trailer_url: 'https://www.youtube.com/watch?v=hXzcyx9V0xw',
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
            trailer_url: 'https://www.youtube.com/watch?v=zSWdZVtXT7E',
            estado: 'disponible'
          }
        ];
        
        const peliculasCombinadas = [...peliculasBackend];
        
        peliculasEstaticas.forEach(peliEstatica => {
          const existe = peliculasCombinadas.some(p => p.id === peliEstatica.id);
          if (!existe) {
            peliculasCombinadas.push(peliEstatica);
          }
        });
        
        this.peliculas = peliculasCombinadas;
        this.peliculasFiltradas = [...this.peliculas];
        this.extraerGeneros();
        this.loading = false;
      },
      error: (error) => {
        console.error('Error al cargar películas:', error);
        
        this.peliculas = [
          {
            id: 1,
            titulo: 'Spider-Man: Across the Spider-Verse',
            descripcion: 'Miles Morales catapulta a través del Multiverso',
            duracion: 140,
            genero: 'Animación',
            clasificacion: 'PG-13',
            imagen_url: 'https://image.tmdb.org/t/p/w500/gh4cZbhZxyTbgxQPxD0dOudNPTn.jpg',
            trailer_url: 'https://www.youtube.com/watch?v=cqGjhVJWtEg',
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
            trailer_url: 'https://www.youtube.com/watch?v=hebWYacbdvc',
            estado: 'cartelera'
          }
        ];
        
        this.peliculasFiltradas = [...this.peliculas];
        this.extraerGeneros();
        this.loading = false;
      }
    });
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

  abrirTrailer(trailerUrl: string | undefined, event?: Event) {
    if (event) {
      event.stopPropagation();
    }
    
    if (trailerUrl && trailerUrl.trim() !== '') {
      window.open(trailerUrl, '_blank', 'noopener,noreferrer');
    } else {
      alert('Esta película no tiene trailer disponible');
    }
  }

  tieneTrailer(pelicula: Pelicula): boolean {
    return !!(pelicula.trailer_url && pelicula.trailer_url.trim() !== '');
  }

  verDetalle(pelicula: Pelicula, event?: Event) {
    if (event) {
      event.stopPropagation();
    }
    this.peliculaSeleccionada = pelicula;
    document.body.style.overflow = 'hidden';
  }

  cerrarDetalle() {
    this.peliculaSeleccionada = null;
    document.body.style.overflow = 'auto';
  }

  editarPelicula(id: number, event?: Event) {
    if (event) {
      event.stopPropagation();
    }
    
    // Verificar permisos antes de navegar
    if (!this.isAdmin) {
      alert('No tienes permisos para editar películas');
      return;
    }
    
    this.router.navigate(['/peliculas/editar', id]);
  }

  eliminarPelicula(id: number, event?: Event) {
    if (event) {
      event.stopPropagation();
    }

    // Verificar permisos antes de eliminar
    if (!this.isAdmin) {
      alert('No tienes permisos para eliminar películas');
      return;
    }

    if (!confirm('¿Estás seguro de que deseas eliminar esta película? Esta acción no se puede deshacer.')) {
      return;
    }

    const token = localStorage.getItem('cinemax_token') || 
                  sessionStorage.getItem('cinemax_token');
    
    const headers = new HttpHeaders({
      'Authorization': `Bearer ${token}`
    });

    this.http.delete(`${this.apiUrl}/${id}`, { headers }).subscribe({
      next: (response: any) => {
        console.log('Película eliminada:', response);
        this.cargarPeliculas();
        alert('Película eliminada exitosamente');
      },
      error: (error) => {
        console.error('Error al eliminar película:', error);
        alert('Error al eliminar la película: ' + (error.error?.message || 'Intenta nuevamente'));
      }
    });
  }

  crearNuevaPelicula() {
    // Verificar permisos antes de navegar
    if (!this.isAdmin) {
      alert('No tienes permisos para crear películas');
      return;
    }
    
    this.router.navigate(['/peliculas/crear']);
  }

  volverDashboard() {
    this.router.navigate(['/dashboard']);
  }
}