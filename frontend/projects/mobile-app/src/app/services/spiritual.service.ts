import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { catchError, tap } from 'rxjs/operators';
import { environment } from '../../environments/environment';

export interface SpiritualLearning {
  source: string;
  title: string;
  explanation: string;
}

export interface SpiritualLesson {
  topic: string;
  quote: string;
  learnings: SpiritualLearning[];
  journal_prompt: string;
}

@Injectable({
  providedIn: 'root'
})
export class SpiritualService {
  private http = inject(HttpClient);
  private apiUrl = `${environment.apiUrl}/spiritual`;

  private cachedLesson: SpiritualLesson | null = null;
  private cacheDate: string | null = null;

  getDailyLesson(): Observable<SpiritualLesson> {
    const today = new Date().toISOString().split('T')[0];
    
    if (this.cachedLesson && this.cacheDate === today) {
      return of(this.cachedLesson);
    }
    
    return this.http.get<SpiritualLesson>(`${this.apiUrl}/daily`).pipe(
      tap(lesson => {
        this.cachedLesson = lesson;
        this.cacheDate = today;
      }),
      catchError(error => {
        console.error('Error fetching spiritual lesson, using offline fallback', error);
        return of(this.getOfflineMockData());
      })
    );
  }

  private getOfflineMockData(): SpiritualLesson {
    return {
      topic: "Offline Fallback: Dharma",
      quote: "You have a right to perform your prescribed duties, but you are not entitled to the fruits of your actions. - Bhagavad Gita",
      learnings: [
        {
          source: "Bhagavad Gita",
          title: "Nishkama Karma",
          explanation: "Do your duty without attachment to the outcome."
        }
      ],
      journal_prompt: "Are my actions driven by ego or duty?"
    };
  }
}
