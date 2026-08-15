import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../environments/environment';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, MatCardModule, MatIconModule, MatButtonModule],
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.scss']
})
export class DashboardComponent implements OnInit {
  private http = inject(HttpClient);
  private apiUrl = environment.apiUrl;

  stats = {
    users: 0,
    activeToday: 0,
    totalContent: 0
  };

  ngOnInit() {
    this.http.get<any>(`${this.apiUrl}/admin/stats`).subscribe({
      next: (data) => {
        this.stats.users = data.users || 0;
        this.stats.activeToday = data.activeToday || 0;
        this.stats.totalContent = data.totalContent || 0;
      },
      error: (err) => {
        console.error('Error fetching admin stats:', err);
      }
    });
  }
}
