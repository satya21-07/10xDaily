import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { environment } from '../../environments/environment';

export interface FinanceLesson {
  id: number;
  topic: string;
  problem?: string;
  solution?: string;
  example?: string;
  calculator_type?: string;
}

export interface HealthLesson {
  id: number;
  category?: string;
  title: string;
  advice?: string;
  scientific_evidence?: string;
  action_step?: string;
}

export interface SpiritualLesson {
  id: number;
  source_text?: string;
  story?: string;
  meaning?: string;
  context?: string;
  modern_example?: string;
  reflection?: string;
}

@Injectable({
  providedIn: 'root'
})
export class LessonsService {
  private http = inject(HttpClient);
  private apiUrl = `${environment.apiUrl}/lessons`;

  getDailyFinance(): Observable<FinanceLesson> {
    return this.http.get<FinanceLesson>(`${this.apiUrl}/finance/daily`).pipe(
      catchError(error => {
        console.error('Error fetching finance lesson', error);
        return of({
          id: 1,
          topic: 'Emergency Fund',
          problem: 'Unexpected expenses can lead to high-interest debt.',
          solution: 'Save 3-6 months of living expenses in a high-yield savings account.',
          example: 'If your monthly expenses are $3,000, aim for $9,000 to $18,000.',
          calculator_type: 'EmergencyFund'
        });
      })
    );
  }

  getDailyHealth(): Observable<HealthLesson> {
    return this.http.get<HealthLesson>(`${this.apiUrl}/health/daily`).pipe(
      catchError(error => {
        console.error('Error fetching health lesson', error);
        return of({
          id: 1,
          category: 'Sleep',
          title: 'The 3-2-1 Rule for Better Sleep',
          advice: 'Stop eating heavy meals 3 hours before bed. Stop working 2 hours before bed. Stop looking at screens 1 hour before bed.',
          scientific_evidence: 'Blue light suppresses melatonin production, delaying sleep onset.',
          action_step: 'Set a "wind-down" alarm 1 hour before your target sleep time.'
        });
      })
    );
  }

  getDailySpiritual(): Observable<SpiritualLesson> {
    return this.http.get<SpiritualLesson>(`${this.apiUrl}/spiritual/daily`).pipe(
      catchError(error => {
        console.error('Error fetching spiritual lesson', error);
        return of({
          id: 1,
          source_text: 'Bhagavad Gita',
          story: 'Arjuna\'s dilemma on the battlefield of Kurukshetra.',
          meaning: 'Perform your duty without attachment to the results.',
          context: 'Focus on the process, not the outcome (Karma Yoga).',
          modern_example: 'Focus on writing good code, not on whether you get promoted.',
          reflection: 'What outcome am I too attached to today?'
        });
      })
    );
  }
}
