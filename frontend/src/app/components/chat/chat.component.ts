import { Component, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import type { ChatResponse } from '../../services/api.service';
import { ApiService } from '../../services/api.service';

interface ChatMessage {
  role: 'user' | 'assistant';
  text: string;
}

@Component({
  selector: 'app-chat',
  standalone: true,
  imports: [FormsModule],
  template: `
    <div class="chat">
      <div class="messages" #messagesBox>
        @for (message of messages(); track $index) {
          <div class="message {{ message.role }}">
            {{ message.text }}
          </div>
        } @empty {
          <div class="placeholder">Preguntale sobre las ventas, por ejemplo: "¿Cuál es la mejor categoría?"</div>
        }
      </div>
      <form class="input-row" (ngSubmit)="send()">
        <input
          [(ngModel)]="question"
          name="question"
          placeholder="Escribí tu pregunta sobre las ventas..."
          autocomplete="off"
        />
        <button type="submit" [disabled]="loading()">Enviar</button>
      </form>
    </div>
  `,
  styles: [
    `
      :host {
        display: block;
        height: 100%;
      }
      .chat {
        display: flex;
        flex-direction: column;
        height: 100%;
        gap: 0.75rem;
      }
      .messages {
        flex: 1;
        overflow-y: auto;
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
        background: rgba(0, 0, 0, 0.25);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 8px;
        padding: 0.75rem;
      }
      .message {
        max-width: 85%;
        padding: 0.5rem 0.75rem;
        border-radius: 10px;
        line-height: 1.4;
        white-space: pre-wrap;
        font-size: 0.9rem;
      }
      .message.user {
        align-self: flex-end;
        background: #2f6fed;
        color: white;
      }
      .message.assistant {
        align-self: flex-start;
        background: rgba(255, 255, 255, 0.08);
        color: #e6ecff;
      }
      .placeholder {
        margin: auto;
        color: #7080a8;
        font-size: 0.9rem;
      }
      .input-row {
        display: flex;
        gap: 0.5rem;
      }
      input {
        flex: 1;
        padding: 0.6rem 0.75rem;
        border-radius: 8px;
        border: 1px solid rgba(255, 255, 255, 0.15);
        background: rgba(255, 255, 255, 0.06);
        color: #e6ecff;
        outline: none;
      }
      button {
        padding: 0.6rem 1rem;
        border-radius: 8px;
        border: none;
        background: #2f6fed;
        color: white;
        cursor: pointer;
      }
      button:disabled {
        opacity: 0.6;
        cursor: not-allowed;
      }
    `,
  ],
})
export class ChatComponent {
  question = '';
  messages = signal<ChatMessage[]>([]);
  loading = signal(false);

  constructor(private api: ApiService) {}

  send(): void {
    const question = this.question.trim();
    if (!question || this.loading()) {
      return;
    }

    this.messages.update((all) => [...all, { role: 'user', text: question }]);
    this.question = '';
    this.loading.set(true);

    this.api.askQuestion(question).subscribe({
      next: (response: ChatResponse) => {
        this.messages.update((all) => [...all, { role: 'assistant', text: response.answer }]);
        this.loading.set(false);
      },
      error: () => {
        this.messages.update((all) => [
          ...all,
          { role: 'assistant', text: 'No se pudo obtener una respuesta del servidor.' },
        ]);
        this.loading.set(false);
      },
    });
  }
}