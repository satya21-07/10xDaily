import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatTabsModule } from '@angular/material/tabs';
import { MatTableModule } from '@angular/material/table';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../environments/environment';

@Component({
  selector: 'app-content-manager',
  standalone: true,
  imports: [CommonModule, MatCardModule, MatTabsModule, MatTableModule, MatButtonModule, MatIconModule],
  templateUrl: './content-manager.component.html',
  styleUrls: ['./content-manager.component.scss']
})
export class ContentManagerComponent implements OnInit {
  private http = inject(HttpClient);
  private apiUrl = environment.apiUrl;

  vocabWords: any[] = [];
  vocabColumns = ['id', 'word', 'difficulty', 'actions'];

  newsArticles: any[] = [];
  newsColumns = ['id', 'title', 'category', 'actions'];

  ngOnInit() {
    this.loadContent();
  }

  loadContent() {
    this.http.get<any[]>(`${this.apiUrl}/vocabulary/daily`).subscribe(data => this.vocabWords = data);
    this.http.get<any[]>(`${this.apiUrl}/news/`).subscribe(data => this.newsArticles = data);
  }
}
