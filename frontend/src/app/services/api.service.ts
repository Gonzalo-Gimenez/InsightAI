import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface VentaItem {
  producto: string;
  categoria: string;
  region: string;
  ventas: number;
}

export interface MetricsResponse {
  total_ventas: number;
  promedio_ventas: number;
  venta_maxima: VentaItem;
  venta_minima: VentaItem;
  ventas_por_categoria: { [categoria: string]: number };
}

export interface ChatResponse {
  answer: string;
}

@Injectable({ providedIn: 'root' })
export class ApiService {
  constructor(private http: HttpClient) {}

  getMetrics(): Observable<MetricsResponse> {
    return this.http.get<MetricsResponse>('/api/v1/metrics');
  }

  askQuestion(question: string): Observable<ChatResponse> {
    return this.http.post<ChatResponse>('/api/v1/chat', { question });
  }
}