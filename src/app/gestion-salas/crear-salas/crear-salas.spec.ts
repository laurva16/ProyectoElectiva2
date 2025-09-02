import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CrearSalas } from './crear-salas';

describe('CrearSalas', () => {
  let component: CrearSalas;
  let fixture: ComponentFixture<CrearSalas>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CrearSalas]
    })
    .compileComponents();

    fixture = TestBed.createComponent(CrearSalas);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
