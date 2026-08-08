import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

export interface QuizQuestion {
  topic: string;
  question: string;
  options: string[];
  correct_index: number;
  explanation: string;
}

export interface QuizResponse {
  questions: QuizQuestion[];
}

@Injectable({
  providedIn: 'root'
})
export class QuizService {
  private http = inject(HttpClient);
  private apiUrl = `${environment.apiUrl}/quiz`;

  getDailyQuiz(): Observable<QuizResponse> {
    return this.http.get<QuizResponse>(`${this.apiUrl}/daily`);
  }
}
