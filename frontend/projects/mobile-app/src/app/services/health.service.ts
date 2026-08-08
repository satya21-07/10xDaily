import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { catchError, tap } from 'rxjs/operators';
import { environment } from '../../environments/environment';

export interface HealthFact {
  title: string;
  explanation: string;
}

export interface Workout {
  name: string;
  duration: string;
  exercises: string[];
}

export interface HealthLesson {
  topic: string;
  workout_of_the_day: Workout;
  health_facts: HealthFact[];
  diet_tip: string;
}

@Injectable({
  providedIn: 'root'
})
export class HealthService {
  private http = inject(HttpClient);
  private apiUrl = `${environment.apiUrl}/health`;

  private cachedLesson: HealthLesson | null = null;
  private cacheDate: string | null = null;

  getDailyLesson(): Observable<HealthLesson> {
    const today = new Date().toISOString().split('T')[0];
    
    if (this.cachedLesson && this.cacheDate === today) {
      return of(this.cachedLesson);
    }
    
    return this.http.get<HealthLesson>(`${this.apiUrl}/daily`).pipe(
      tap(lesson => {
        this.cachedLesson = lesson;
        this.cacheDate = today;
      }),
      catchError(error => {
        console.error('Error fetching health lesson, using offline fallback', error);
        return of(this.getOfflineMockData());
      })
    );
  }

  private getOfflineMockData(): HealthLesson {
    return {
      topic: "Offline Fallback: Hydration",
      workout_of_the_day: {
        name: "Stretching",
        duration: "5 mins",
        exercises: ["Stretch 1", "Stretch 2"]
      },
      health_facts: [
        {
          title: "Water",
          explanation: "Drink water."
        }
      ],
      diet_tip: "Drink a glass of water right when you wake up."
    };
  }
}
