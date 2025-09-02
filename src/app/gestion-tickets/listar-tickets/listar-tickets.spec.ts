import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ListarTickets } from './listar-tickets';

describe('ListarTickets', () => {
  let component: ListarTickets;
  let fixture: ComponentFixture<ListarTickets>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ListarTickets]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ListarTickets);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
