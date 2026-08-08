import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { catchError, tap } from 'rxjs/operators';
import { environment } from '../../environments/environment';

export interface FinanceConcept {
  title: string;
  explanation: string;
}

export interface FinanceLesson {
  topic: string;
  daily_tip: string;
  concepts: FinanceConcept[];
  action_item: string;
}

@Injectable({
  providedIn: 'root'
})
export class FinanceService {
  private http = inject(HttpClient);
  private apiUrl = `${environment.apiUrl}/finance`;

  private cachedLesson: FinanceLesson | null = null;
  private cacheDate: string | null = null;

  getDailyLesson(): Observable<FinanceLesson> {
    const today = new Date().toISOString().split('T')[0];
    
    if (this.cachedLesson && this.cacheDate === today) {
      return of(this.cachedLesson);
    }
    
    return this.http.get<FinanceLesson>(`${this.apiUrl}/daily`).pipe(
      tap(lesson => {
        this.cachedLesson = lesson;
        this.cacheDate = today;
      }),
      catchError(error => {
        console.error('Error fetching finance lesson, using offline fallback', error);
        return of(this.getOfflineMockData());
      })
    );
  }

  private getOfflineMockData(): FinanceLesson {
    return {
      topic: "Offline Fallback: Budgeting",
      daily_tip: "Track every penny for 30 days.",
      concepts: [
        {
          title: "The 50/30/20 Rule",
          explanation: "50% Needs, 30% Wants, 20% Savings."
        }
      ],
      action_item: "Set up a spreadsheet to track your expenses."
    };
  }
}
