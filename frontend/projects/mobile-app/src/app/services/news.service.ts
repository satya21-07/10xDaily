import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { NewsArticle } from '../models/news.model';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class NewsService {
  private http = inject(HttpClient);
  private apiUrl = `${environment.apiUrl}/news`;

  getNews(category?: string, skip: number = 0, limit: number = 10): Observable<NewsArticle[]> {
    let url = `${this.apiUrl}/?skip=${skip}&limit=${limit}`;
    if (category) {
      url += `&category=${category}`;
    }
    return this.http.get<NewsArticle[]>(url).pipe(
      catchError(error => {
        console.error('Error fetching news, using offline fallback', error);
        return of(this.getOfflineMockData());
      })
    );
  }

  private getOfflineMockData(): NewsArticle[] {
    return [
      {
        id: 1,
        title: 'OpenAI announces GPT-5 release window',
        summary: 'The highly anticipated AI model is expected to launch late this year, promising significant improvements in reasoning and multi-modal capabilities.',
        source: 'TechCrunch',
        category: 'AI',
        image_url: 'https://images.unsplash.com/photo-1677442136019-21780ecad995?auto=format&fit=crop&q=80&w=800',
        published_at: new Date().toISOString(),
        ai_summary: 'GPT-5 is coming later this year with better reasoning.'
      },
      {
        id: 2,
        title: 'Global Markets Rally on Tech Earnings',
        summary: 'Major indices hit record highs today following stronger-than-expected quarterly earnings from leading technology companies.',
        source: 'Bloomberg',
        category: 'Business',
        image_url: 'https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?auto=format&fit=crop&q=80&w=800',
        published_at: new Date().toISOString(),
        ai_summary: 'Tech earnings push stock market to all-time highs.'
      }
    ];
  }
}
