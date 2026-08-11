import { Injectable, inject } from '@angular/core';
import { AuthService } from './auth.service';
import { HttpClient } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { catchError, tap } from 'rxjs/operators';
import { environment } from '../../environments/environment';

export interface HealthFact {
  title: string;
  explanation: string;
  key_points: string[];
}

export interface DailyExercise {
  name: string;
  duration: string;
  instructions: string;
  safety_note?: string;
}

export interface DailyActivity {
  name: string;
  duration: string;
  level: string;
  exercises: DailyExercise[];
}

export interface FeaturedFood {
  name: string;
  calories: string;
  protein: string;
  carbs: string;
  fat: string;
  fiber: string;
}

export interface NutritionTip {
  title: string;
  description: string;
  featured_foods?: FeaturedFood[];
}

export interface DailyHabit {
  title: string;
  description: string;
}

export interface HealthSource {
  name: string;
  url: string;
  type: string;
  retrieved_at: string;
}

export interface HealthLesson {
  id?: number;
  lesson_date?: string;
  topic: string;
  learning_objective: string;
  health_facts: HealthFact[];
  daily_activity: DailyActivity;
  nutrition_tip: NutritionTip;
  daily_habit: DailyHabit;
  source: HealthSource;
  disclaimer: string;
}

@Injectable({
  providedIn: 'root'
})
export class HealthService {
  private http = inject(HttpClient);
  private authService = inject(AuthService);
  private currentUserId: string | number | null = null;
  private apiUrl = `${environment.apiUrl}/health`;

  private cachedLesson: HealthLesson | null = null;
  private cacheDate: string | null = null;


  constructor() {
    this.authService.currentUser$.subscribe(user => {
      const newUserId = user?.id || null;
      if (this.currentUserId !== newUserId) {
        this.currentUserId = newUserId;
        this.cachedLesson = null;
        this.cacheDate = null;
      }
    });
  }
  getDailyLesson(): Observable<HealthLesson> {
    const today = new Date().toISOString().split('T')[0];
    
    if (this.cachedLesson && this.cacheDate === today) {
      return of(JSON.parse(JSON.stringify(this.cachedLesson)));
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
      learning_objective: "Understand the importance of hydration.",
      health_facts: [
        {
          title: "Water and energy",
          explanation: "Dehydration can significantly reduce your energy levels.",
          key_points: ["Drink water", "Stay hydrated"]
        }
      ],
      daily_activity: {
        name: "Stretching",
        duration: "5 mins",
        level: "Beginner",
        exercises: [
          {
            name: "Neck rolls",
            duration: "1 min",
            instructions: "Roll your neck slowly.",
            safety_note: "Stop if you feel pain."
          }
        ]
      },
      nutrition_tip: {
        title: "Drink a glass of water right when you wake up.",
        description: "It helps kickstart your metabolism, flushes out toxins that have accumulated overnight, and gives your brain the hydration it needs to stay focused.",
        featured_foods: [
          {
            name: "Water",
            calories: "0 kcal",
            protein: "0g",
            carbs: "0g",
            fat: "0g",
            fiber: "0g"
          }
        ]
      },
      daily_habit: {
        title: "Carry a water bottle",
        description: "Keep it with you all day."
      },
      source: {
        name: "10xDaily General Wellness",
        url: "",
        type: "fallback",
        retrieved_at: ""
      },
      disclaimer: "This content is for general educational purposes and is not medical advice."
    };
  }
}
