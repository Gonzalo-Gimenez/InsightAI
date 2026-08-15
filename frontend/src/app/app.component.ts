import { Component, OnInit, signal } from '@angular/core';
import { ApiService, MetricsResponse } from './services/api.service';
import { Chart3dComponent } from './components/chart3d/chart3d.component';
import { ChatComponent } from './components/chat/chat.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [Chart3dComponent, ChatComponent],
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss',
})
export class AppComponent implements OnInit {
  metrics = signal<MetricsResponse | null>(null);
  error = signal<string | null>(null);

  constructor(private api: ApiService) {}

  ngOnInit(): void {
    this.api
      .getMetrics()
      .subscribe({
        next: (m) => this.metrics.set(m),
        error: () => this.error.set('No se pudo conectar con la API. Asegurate de que el backend esté corriendo en http://127.0.0.1:8000'),
      });
  }
}