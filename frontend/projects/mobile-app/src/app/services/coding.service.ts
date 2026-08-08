import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { catchError, tap } from 'rxjs/operators';
import { environment } from '../../environments/environment';

export interface CodingConcept {
  title: string;
  explanation: string;
}

export interface CodingQuestion {
  title: string;
  description: string;
  difficulty: string;
  hint: string;
  solution_java?: string;
  solution_python?: string;
}

export interface CodingLesson {
  topic: string;
  concepts: CodingConcept[];
  questions: CodingQuestion[];
}

@Injectable({
  providedIn: 'root'
})
export class CodingService {
  private http = inject(HttpClient);
  private apiUrl = `${environment.apiUrl}/coding`;

  private cachedLesson: CodingLesson | null = null;
  private cacheDate: string | null = null;

  getDailyLesson(): Observable<CodingLesson> {
    const today = new Date().toISOString().split('T')[0];
    
    if (this.cachedLesson && this.cacheDate === today) {
      return of(this.cachedLesson);
    }
    
    return this.http.get<CodingLesson>(`${this.apiUrl}/daily`).pipe(
      tap(lesson => {
        this.cachedLesson = lesson;
        this.cacheDate = today;
      }),
      catchError(error => {
        console.error('Error fetching coding lesson, using offline fallback', error);
        return of(this.getOfflineMockData());
      })
    );
  }

  private getOfflineMockData(): CodingLesson {
    return {
      topic: "Offline Fallback: Arrays",
      concepts: [
        {
          title: "Arrays",
          explanation: "An array is a collection of items stored at contiguous memory locations."
        }
      ],
      questions: [
        {
          title: "Two Sum",
          description: "Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.",
          difficulty: "Easy",
          hint: "Use a hash map to store elements you've seen."
        }
      ]
    };
  }
}
