import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatTabsModule } from '@angular/material/tabs';
import { MatTableModule } from '@angular/material/table';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatChipsModule } from '@angular/material/chips';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../environments/environment';

@Component({
  selector: 'app-content-manager',
  standalone: true,
  imports: [CommonModule, MatCardModule, MatTabsModule, MatTableModule, MatButtonModule, MatIconModule, MatChipsModule],
  templateUrl: './content-manager.component.html',
  styleUrls: ['./content-manager.component.scss']
})
export class ContentManagerComponent implements OnInit {
  private http = inject(HttpClient);
  private apiUrl = environment.apiUrl;

  contentSummary: any = {};
  topics: any[] = [];
  topicColumns = ['id', 'name', 'description', 'is_default', 'subscribed_users'];
  
  gamification: any[] = [];
  gamificationColumns = ['id', 'full_name', 'email', 'games_played', 'last_played', 'status'];

  vocabWords: any[] = [];
  vocabColumns = ['id', 'word', 'difficulty', 'source'];

  newsArticles: any[] = [];
  newsColumns = ['id', 'title', 'category', 'user_name', 'saved_at'];

  gameHistory: any[] = [];
  gameHistoryColumns = ['id', 'user_name', 'game_name', 'score', 'completion_date'];

  bookmarks: any[] = [];
  bookmarkColumns = ['id', 'title', 'content_type', 'folder', 'user_name'];

  notes: any[] = [];
  noteColumns = ['id', 'title', 'content', 'user_name'];

  ngOnInit() {
    this.loadContent();
  }

  loadContent() {
    this.http.get<any>(`${this.apiUrl}/admin/content-summary`).subscribe({
      next: (data) => this.contentSummary = data,
      error: (err) => console.error('Error fetching content summary', err)
    });

    this.http.get<any[]>(`${this.apiUrl}/admin/topics`).subscribe({
      next: (data) => this.topics = data,
      error: (err) => console.error('Error fetching topics', err)
    });

    this.http.get<any[]>(`${this.apiUrl}/admin/gamification`).subscribe({
      next: (data) => this.gamification = data,
      error: (err) => console.error('Error fetching gamification', err)
    });

    this.http.get<any[]>(`${this.apiUrl}/admin/vocabulary`).subscribe({
      next: (data) => this.vocabWords = data,
      error: (err) => console.error('Error fetching vocabulary', err)
    });

    this.http.get<any[]>(`${this.apiUrl}/admin/news`).subscribe({
      next: (data) => this.newsArticles = data,
      error: (err) => console.error('Error fetching news', err)
    });

    this.http.get<any[]>(`${this.apiUrl}/admin/games-history`).subscribe({
      next: (data) => this.gameHistory = data,
      error: (err) => console.error('Error fetching games history', err)
    });

    this.http.get<any[]>(`${this.apiUrl}/admin/bookmarks`).subscribe({
      next: (data) => this.bookmarks = data,
      error: (err) => console.error('Error fetching bookmarks', err)
    });

    this.http.get<any[]>(`${this.apiUrl}/admin/notes`).subscribe({
      next: (data) => this.notes = data,
      error: (err) => console.error('Error fetching notes', err)
    });
  }
}
