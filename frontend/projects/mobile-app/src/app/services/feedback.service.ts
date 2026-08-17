import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { FeedbackRequest, FeedbackItem } from '../models/feedback.model';

@Injectable({
  providedIn: 'root'
})
export class FeedbackService {
  private http = inject(HttpClient);
  private apiUrl = `${environment.apiUrl}/feedback`;

  submitFeedback(feedback: FeedbackRequest): Observable<FeedbackItem> {
    return this.http.post<FeedbackItem>(`${this.apiUrl}/`, feedback);
  }

  getMyFeedback(skip = 0, limit = 20): Observable<FeedbackItem[]> {
    return this.http.get<FeedbackItem[]>(`${this.apiUrl}/my-feedback?skip=${skip}&limit=${limit}`);
  }
}
