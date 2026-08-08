import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { catchError } from 'rxjs/operators';
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

  getRandomQuote(): Observable<DailyQuote> {
    return this.http.get<DailyQuote>(`${this.apiUrl}/random`).pipe(
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
