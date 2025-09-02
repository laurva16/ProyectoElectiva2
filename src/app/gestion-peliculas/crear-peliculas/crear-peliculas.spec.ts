import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CrearPeliculas } from './crear-peliculas';

describe('CrearPeliculas', () => {
  let component: CrearPeliculas;
  let fixture: ComponentFixture<CrearPeliculas>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CrearPeliculas]
    })
    .compileComponents();

    fixture = TestBed.createComponent(CrearPeliculas);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
