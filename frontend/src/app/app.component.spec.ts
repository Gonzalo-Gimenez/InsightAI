import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { AppComponent } from './app.component';

const MOCK_METRICS = {
  total_ventas: 2200,
  promedio_ventas: 440,
  venta_maxima: { producto: 'Laptop', categoria: 'Electrónica', region: 'Norte', ventas: 1500 },
  venta_minima: { producto: 'Teclado', categoria: 'Accesorios', region: 'Norte', ventas: 80 },
  ventas_por_categoria: { Electrónica: 1800, Accesorios: 200, Oficina: 200 },
};

describe('AppComponent', () => {
  let httpMock: HttpTestingController;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AppComponent, HttpClientTestingModule],
    }).compileComponents();
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();
  });

  it('should create the app', () => {
    const fixture = TestBed.createComponent(AppComponent);
    expect(fixture.componentInstance).toBeTruthy();
  });

  it('carga las métricas al inicializar', () => {
    const fixture = TestBed.createComponent(AppComponent);
    fixture.detectChanges();

    const req = httpMock.expectOne('/api/v1/metrics');
    expect(req.request.method).toBe('GET');
    req.flush(MOCK_METRICS);
    fixture.detectChanges();

    expect(fixture.componentInstance.metrics()?.total_ventas).toBe(2200);
  });

  it('muestra el título', () => {
    const fixture = TestBed.createComponent(AppComponent);
    fixture.detectChanges();

    const req = httpMock.expectOne('/api/v1/metrics');
    req.flush(MOCK_METRICS);
    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.querySelector('h1')?.textContent).toContain('InsightAI');
  });
});