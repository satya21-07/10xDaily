import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { catchError, tap } from 'rxjs/operators';
import { environment } from '../../environments/environment';

export interface OnThisDayEvent {
  date: string;
  month: number;
  day: number;
  year: number | string;
  title: string;
  description: string;
  category: string;
  country: string;
  source_name: string;
  source_url?: string;
  image_url?: string;
  why_it_matters?: string;
}

@Injectable({
  providedIn: 'root'
})
export class OnThisDayService {
  private http = inject(HttpClient);
  private apiUrl = `${environment.apiUrl}/on-this-day`;
  private readonly CACHE_KEY = 'on_this_day_cache_v2';
  private readonly DATE_KEY = 'on_this_day_date_v2';

  getTodayEvent(): Observable<OnThisDayEvent> {
    const today = new Date().toDateString();
    const cachedDate = localStorage.getItem(this.DATE_KEY);
    
    if (cachedDate === today) {
      const cachedEvent = localStorage.getItem(this.CACHE_KEY);
      if (cachedEvent) {
        return of(JSON.parse(cachedEvent));
      }
    }

    return this.http.get<OnThisDayEvent>(`${this.apiUrl}/today`).pipe(
      tap(event => {
        localStorage.setItem(this.CACHE_KEY, JSON.stringify(event));
        localStorage.setItem(this.DATE_KEY, today);
      }),
      catchError(error => {
        console.error('Error fetching on this day event, using offline fallback', error);
        return of(this.getOfflineMockData());
      })
    );
  }

  private getOfflineMockData(): OnThisDayEvent {
    const today = new Date();
    return {
      date: today.toISOString().split('T')[0],
      month: today.getMonth() + 1,
      day: today.getDate(),
      year: 1969,
      title: "Apollo 11 Moon Landing",
      description: "American astronauts Neil Armstrong and Buzz Aldrin became the first humans to walk on the Moon.",
      category: "Science & Technology",
      country: "World",
      source_name: "Fallback Data",
      image_url: "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1e/Apollo_11_first_step.jpg/440px-Apollo_11_first_step.jpg",
      why_it_matters: "A monumental achievement in human history and space exploration."
    };
  }
}
