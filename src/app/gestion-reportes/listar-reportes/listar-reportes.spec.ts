import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ListarReportes } from './listar-reportes';

describe('ListarReportes', () => {
  let component: ListarReportes;
  let fixture: ComponentFixture<ListarReportes>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ListarReportes]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ListarReportes);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
