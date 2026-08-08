import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
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

  constructor(private http: HttpClient) { }

  getBookmarks(): Observable<Bookmark[]> {
    return this.http.get<Bookmark[]>(this.apiUrl);
  }

  saveBookmark(bookmark: Bookmark): Observable<Bookmark> {
    return this.http.post<Bookmark>(this.apiUrl, bookmark);
  }

  deleteBookmark(id: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/${id}`);
  }
}
