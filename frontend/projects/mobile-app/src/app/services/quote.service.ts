import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { catchError, tap } from 'rxjs/operators';
import { environment } from '../../environments/environment';

export interface DailyQuote {
  text: string;
  author: string;
}

@Injectable({
  providedIn: 'root'
})
export class QuoteService {
  private http = inject(HttpClient);
  private apiUrl = `${environment.apiUrl}/quote`;
  private readonly CACHE_KEY = 'daily_quote_cache';
  private readonly DATE_KEY = 'daily_quote_date';

  getRandomQuote(): Observable<DailyQuote> {
    const today = new Date().toDateString();
    const cachedDate = localStorage.getItem(this.DATE_KEY);
    
    if (cachedDate === today) {
      const cachedQuote = localStorage.getItem(this.CACHE_KEY);
      if (cachedQuote) {
        return of(JSON.parse(cachedQuote));
      }
    }

    return this.http.get<DailyQuote>(`${this.apiUrl}/random`).pipe(
      tap(quote => {
        localStorage.setItem(this.CACHE_KEY, JSON.stringify(quote));
        localStorage.setItem(this.DATE_KEY, today);
      }),
      catchError(error => {
        console.error('Error fetching random quote, using offline fallback', error);
        return of(this.getOfflineMockData());
      })
    );
  }

  private getOfflineMockData(): DailyQuote {
    return {
      text: "The only way to do great work is to love what you do.",
      author: "Steve Jobs"
    };
  }
}
