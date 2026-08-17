import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { NewsArticle, SavedNewsResponse } from '../models/news.model';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class NewsService {
  private http = inject(HttpClient);
  private apiUrl = `${environment.apiUrl}/news`;

  getNews(category?: string, skip: number = 0, limit: number = 20): Observable<NewsArticle[]> {
    let url = `${this.apiUrl}?skip=${skip}&limit=${limit}`;
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

  getFullStory(url: string, title: string, summary?: string, source?: string, category?: string): Observable<{
    content: string;
    summary?: string;
    key_highlights?: string[];
    full_coverage?: string[];
    why_it_matters?: string;
  }> {
    const params: any = { url, title };
    if (summary) params.summary = summary;
    if (source) params.source = source;
    if (category) params.category = category;
    return this.http.get<{
      content: string;
      summary?: string;
      key_highlights?: string[];
      full_coverage?: string[];
      why_it_matters?: string;
    }>(`${this.apiUrl}/full-story`, { params }).pipe(
      catchError(err => {
        console.error('Error fetching full story:', err);
        return of({ content: summary || title, summary: summary || title });
      })
    );
  }

  getSavedNews(skip: number = 0, limit: number = 50): Observable<SavedNewsResponse[]> {
    return this.http.get<SavedNewsResponse[]>(`${this.apiUrl}/saved?skip=${skip}&limit=${limit}`);
  }

  saveArticle(article: NewsArticle): Observable<SavedNewsResponse> {
    return this.http.post<SavedNewsResponse>(`${this.apiUrl}/${article.id}/save`, article);
  }

  unsaveArticle(articleId: string, url: string): Observable<any> {
    return this.http.delete(`${this.apiUrl}/${articleId}/save?url=${encodeURIComponent(url)}`);
  }

  private getOfflineMockData(): NewsArticle[] {
    return [
      {
        id: "1",
        title: 'OpenAI announces GPT-5 release window',
        summary: 'The highly anticipated AI model is expected to launch late this year, promising significant improvements in reasoning and multi-modal capabilities.',
        source: 'TechCrunch',
        category: 'AI',
        image_url: 'https://images.unsplash.com/photo-1677442136019-21780ecad995?auto=format&fit=crop&q=80&w=800',
        published_at: new Date().toISOString(),
        ai_summary: 'GPT-5 is coming later this year with better reasoning.',
        is_saved: false,
        url: 'https://example.com/ai'
      },
      {
        id: "2",
        title: 'Global Markets Rally on Tech Earnings',
        summary: 'Major indices hit record highs today following stronger-than-expected quarterly earnings from leading technology companies.',
        source: 'Bloomberg',
        category: 'Business',
        image_url: 'https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?auto=format&fit=crop&q=80&w=800',
        published_at: new Date().toISOString(),
        ai_summary: 'Tech earnings push stock market to all-time highs.',
        is_saved: false,
        url: 'https://example.com/markets'
      }
    ];
  }
}
