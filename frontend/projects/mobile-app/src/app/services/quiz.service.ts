import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { tap } from 'rxjs/operators';
import { environment } from '../../environments/environment';
import { AuthService } from './auth.service';

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
  private authService = inject(AuthService);
  private apiUrl = `${environment.apiUrl}/quiz`;

  private currentUserId: string | number | null = null;
  private cachedQuiz: QuizResponse | null = null;
  private cacheDate: string | null = null;
  
  private cachedProgress: QuizProgressResponse | null = null;
  private progressCacheDate: string | null = null;

  constructor() {
    this.authService.currentUser$.subscribe(user => {
      const newUserId = user?.id || null;
      if (this.currentUserId !== newUserId) {
        this.currentUserId = newUserId;
        this.cachedQuiz = null;
        this.cacheDate = null;
        this.cachedProgress = null;
        this.progressCacheDate = null;
      }
    });
  }

  getDailyQuiz(): Observable<QuizResponse> {
    const today = new Date().toISOString().split('T')[0];
    
    if (this.cachedQuiz && this.cacheDate === today) {
      return of(JSON.parse(JSON.stringify(this.cachedQuiz)));
    }
    
    return this.http.get<QuizResponse>(`${this.apiUrl}/daily`).pipe(
      tap(quiz => {
        this.cachedQuiz = quiz;
        this.cacheDate = today;
      })
    );
  }

  getTodayProgress(): Observable<QuizProgressResponse> {
    const today = new Date().toISOString().split('T')[0];
    
    if (this.cachedProgress && this.progressCacheDate === today) {
      return of(JSON.parse(JSON.stringify(this.cachedProgress)));
    }
    
    return this.http.get<QuizProgressResponse>(`${this.apiUrl}/progress/today`).pipe(
      tap(prog => {
        this.cachedProgress = prog;
        this.progressCacheDate = today;
      })
    );
  }

  saveProgress(state: QuizStateUpdate): Observable<any> {
    const today = new Date().toISOString().split('T')[0];
    this.cachedProgress = {
      completed: state.is_finished,
      saved_state: state
    };
    this.progressCacheDate = today;
    
    return this.http.post(`${this.apiUrl}/progress/complete`, state);
  }
}
