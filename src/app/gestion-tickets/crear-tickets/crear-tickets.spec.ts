import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CrearTickets } from './crear-tickets';

describe('CrearTickets', () => {
  let component: CrearTickets;
  let fixture: ComponentFixture<CrearTickets>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CrearTickets]
    })
    .compileComponents();

    fixture = TestBed.createComponent(CrearTickets);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
