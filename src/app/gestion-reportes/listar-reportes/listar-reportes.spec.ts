import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { provideRouter } from '@angular/router';
import { provideZoneChangeDetection } from '@angular/core';
import { ListarReportes } from './listar-reportes';

describe('ListarReportes', () => {
  let component: ListarReportes;
  let fixture: ComponentFixture<ListarReportes>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ListarReportes],
      providers: [
        provideZoneChangeDetection({ eventCoalescing: true }),
        provideHttpClient(),
        provideRouter([])
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(ListarReportes);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should initialize dates on init', () => {
    expect(component.fechaInicio).toBeTruthy();
    expect(component.fechaFin).toBeTruthy();
  });
});