import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { catchError, tap } from 'rxjs/operators';
import { environment } from '../../environments/environment';

export interface SpiritualSource {
  name: string;
  reference: string;
  chapter?: number | null;
  verse?: number | null;
  translation?: string | null;  // The actual scripture passage text from DB
  character?: string | null;    // Speaker e.g. Krishna, Hanuman
  section?: string | null;      // e.g. Sundara Kanda, Chapter 2
}

export interface SpiritualReflection {
  title: string;
  explanation: string;
  key_takeaways: string[];
}

export interface TodayPractice {
  title: string;
  description: string;
}

export interface SpiritualLesson {
  lesson_date: string;
  topic: string;
  source: SpiritualSource;
  reflection: SpiritualReflection;
  today_practice: TodayPractice;
  journal_prompt: string;
}

@Injectable({
  providedIn: 'root'
})
export class SpiritualService {
  private http = inject(HttpClient);
  private apiUrl = `${environment.apiUrl}/spiritual`;

  private cachedLesson: SpiritualLesson | null = null;

  getDailyLesson(): Observable<SpiritualLesson> {
    const today = new Date().toISOString().split('T')[0];
    
    if (this.cachedLesson && this.cachedLesson.lesson_date === today) {
      return of(this.cachedLesson);
    }
    
    return this.http.get<SpiritualLesson>(`${this.apiUrl}/daily`).pipe(
      tap(lesson => {
        this.cachedLesson = lesson;
      }),
      catchError(error => {
        console.error('Error fetching spiritual lesson, using offline fallback', error);
        return of(this.getOfflineMockData(today));
      })
    );
  }

  private getOfflineMockData(today: string): SpiritualLesson {
    return {
      lesson_date: today,
      topic: "Karma",
      source: {
        name: "Bhagavad Gita",
        reference: "Bhagavad Gita 2.47",
        chapter: 2,
        verse: 47,
        section: "Chapter 2",
        character: "Krishna",
        translation: "You have a right to perform your prescribed duties, but you are not entitled to the fruits of your actions. Never consider yourself to be the cause of the results of your activities, nor be attached to inaction."
      },
      reflection: {
        title: "Nishkama Karma — Action Without Attachment",
        explanation: "In the second chapter of the Bhagavad Gita, Krishna delivers one of the most transformative teachings in world philosophy. Arjuna stands frozen on the battlefield of Kurukshetra, unable to fight because he fears the outcome.\n\nKrishna's response cuts to the root of all human suffering: we suffer because we are attached to results rather than the quality of our effort. You have a right to act — but you do not own the outcome.\n\nNishkama karma (desireless action) is not passivity; it is the art of giving your absolute best without making your peace of mind contingent on the result.",
        key_takeaways: [
          "Your job is to act with full effort — the outcome is beyond your control",
          "Attachment to results distorts your judgment and creates anxiety",
          "Detachment from outcomes paradoxically leads to better performance",
          "Focus on the quality of your action, not the reward it might bring"
        ]
      },
      today_practice: {
        title: "One Task, Full Effort",
        description: "Choose the most important task on your plate today. Before beginning, silently commit: 'I will give this my complete attention and best effort. Whatever happens after is not mine to control.' Notice how this changes your relationship to the work itself."
      },
      journal_prompt: "Think of a situation where fear of a bad outcome stopped you from acting well. What would you have done differently if you had been fully detached from the result?"
    };
  }
}
