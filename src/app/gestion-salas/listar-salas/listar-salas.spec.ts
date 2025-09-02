import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ListarSalas } from './listar-salas';

describe('ListarSalas', () => {
  let component: ListarSalas;
  let fixture: ComponentFixture<ListarSalas>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ListarSalas]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ListarSalas);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
