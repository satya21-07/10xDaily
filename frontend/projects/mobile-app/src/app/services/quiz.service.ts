import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

export interface QuizQuestion {
  id: string;
  topic: string;
  difficulty: string;
  question: string;
  options: string[];
  correct_index: number;
  explanation: string;
}

export interface QuizResponse {
  questions: QuizQuestion[];
}

export interface QuizStateUpdate {
  user_answers: (number | null)[];
  score: number;
  is_finished: boolean;
  stats_synced: boolean;
}

export interface QuizProgressResponse {
  completed: boolean;
  saved_state: QuizStateUpdate | null;
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

  getTodayProgress(): Observable<QuizProgressResponse> {
    return this.http.get<QuizProgressResponse>(`${this.apiUrl}/progress/today`);
  }

  saveProgress(state: QuizStateUpdate): Observable<any> {
    return this.http.post(`${this.apiUrl}/progress/complete`, state);
  }
}
