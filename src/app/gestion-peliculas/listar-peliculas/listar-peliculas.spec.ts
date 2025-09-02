import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ListarPeliculas } from './listar-peliculas';

describe('ListarPeliculas', () => {
  let component: ListarPeliculas;
  let fixture: ComponentFixture<ListarPeliculas>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ListarPeliculas]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ListarPeliculas);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
