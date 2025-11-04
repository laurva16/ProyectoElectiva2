import { provideZonelessChangeDetection } from '@angular/core';
import { TestBed } from '@angular/core/testing';
import { AppComponent } from './app';  // ✅ Cambiado de App a AppComponent

describe('AppComponent', () => {  // ✅ Cambiado el nombre del describe
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AppComponent],  // ✅ Cambiado de App a AppComponent
      providers: [provideZonelessChangeDetection()]
    }).compileComponents();
  });

  it('should create the app', () => {
    const fixture = TestBed.createComponent(AppComponent);  // ✅ Cambiado
    const app = fixture.componentInstance;
    expect(app).toBeTruthy();
  });

  it(`should have the 'ProyectoElectiva2' title`, () => {
    const fixture = TestBed.createComponent(AppComponent);  // ✅ Cambiado
    const app = fixture.componentInstance;
    expect(app.title).toEqual('ProyectoElectiva2');
  });

  it('should render router outlet', () => {
    const fixture = TestBed.createComponent(AppComponent);  // ✅ Cambiado
    fixture.detectChanges();
    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.querySelector('router-outlet')).toBeTruthy();
  });
});