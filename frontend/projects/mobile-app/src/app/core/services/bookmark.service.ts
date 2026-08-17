import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, BehaviorSubject, of } from 'rxjs';
import { tap } from 'rxjs/operators';
import { environment } from '../../../environments/environment';

export interface Bookmark {
  id?: number;
  title: string;
  url?: string;
  content_type: string;
  reference_id?: string;
  folder?: string;
  details?: string;
  parsed_data?: any;
  created_at?: string;
}

@Injectable({
  providedIn: 'root'
})
export class BookmarkService {
  private apiUrl = `${environment.apiUrl}/bookmarks`;
  private bookmarksSubject = new BehaviorSubject<Bookmark[] | null>(null);

  constructor(private http: HttpClient) { }

  getBookmarks(forceRefresh: boolean = false): Observable<Bookmark[]> {
    if (!forceRefresh && this.bookmarksSubject.value !== null) {
      return of(this.bookmarksSubject.value);
    }
    return this.http.get<Bookmark[]>(this.apiUrl).pipe(
      tap(bookmarks => this.bookmarksSubject.next(bookmarks))
    );
  }

  saveBookmark(bookmark: Bookmark): Observable<Bookmark> {
    return this.http.post<Bookmark>(this.apiUrl, bookmark).pipe(
      tap(newBookmark => {
        const current = this.bookmarksSubject.value || [];
        this.bookmarksSubject.next([newBookmark, ...current.filter(b => b.id !== newBookmark.id)]);
      })
    );
  }

  deleteBookmark(id: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/${id}`).pipe(
      tap(() => {
        const current = this.bookmarksSubject.value || [];
        this.bookmarksSubject.next(current.filter(b => b.id !== id));
      })
    );
  }

  clearCache(): void {
    this.bookmarksSubject.next(null);
  }
}

