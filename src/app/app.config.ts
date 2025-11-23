// src/app/app.config.ts
import { ApplicationConfig, provideZoneChangeDetection } from '@angular/core';
import { provideRouter } from '@angular/router';
import { provideHttpClient } from '@angular/common/http';
import { routes } from './app.routes';

export const appConfig: ApplicationConfig = {
  providers: [
    provideZoneChangeDetection({ eventCoalescing: true }),
    provideRouter(routes),
    provideHttpClient()
  ]
};

// Configuración de la API (separada)
export const API_CONFIG = {
  AWS_URL: 'https://8g12ab6b23.execute-api.us-east-1.amazonaws.com/dev/api',
  LOCAL_URL: 'http://localhost:5000/api',
  
  get BASE_URL(): string {
    return this.AWS_URL;  // ← Usar AWS
  }
};