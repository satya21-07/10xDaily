import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { MatTableModule } from '@angular/material/table';
import { MatButtonModule } from '@angular/material/button';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { MatTooltipModule } from '@angular/material/tooltip';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { environment } from '../../../environments/environment';
import { UserDetailsDialogComponent } from './components/user-details-dialog/user-details-dialog.component';

export interface User {
  id: number;
  email: string;
  full_name: string;
  is_active: boolean;
  is_superuser: boolean;
  created_at: string;
  last_login_at: string | null;
  phone_number: string | null;
  date_of_birth: string | null;
  xp: number;
  current_streak: number;
  words_learned: number;
  quiz_correct_answers: number;
  quiz_total_answers: number;
  modules_completed: number;
  modules_explored: number;
  total_time_spent_seconds: number;
  avatar: string | null;
}

@Component({
  selector: 'app-users',
  standalone: true,
  imports: [CommonModule, MatCardModule, MatIconModule, MatTableModule, MatButtonModule, MatDialogModule, MatTooltipModule],
  templateUrl: './users.component.html',
  styleUrls: ['./users.component.scss']
})
export class UsersComponent implements OnInit {
  private http = inject(HttpClient);
  private dialog = inject(MatDialog);
  private apiUrl = environment.apiUrl;

  users: User[] = [];
  displayedColumns: string[] = ['id', 'email', 'full_name', 'status', 'created_at', 'last_login', 'xp', 'actions'];
  
  stats = {
    totalUsers: 0,
    activeToday: 0,
    activeThisWeek: 0
  };

  ngOnInit() {
    this.fetchUsers();
  }

  fetchUsers() {
    this.http.get<User[]>(`${this.apiUrl}/users?limit=1000`).subscribe({
      next: (data) => {
        this.users = data;
        this.calculateStats(data);
      },
      error: (err) => {
        console.error('Error fetching users:', err);
      }
    });
  }

  calculateStats(users: User[]) {
    this.stats.totalUsers = users.length;
    
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    
    const lastWeek = new Date();
    lastWeek.setDate(lastWeek.getDate() - 7);
    lastWeek.setHours(0, 0, 0, 0);

    let activeTodayCount = 0;
    let activeThisWeekCount = 0;

    users.forEach(u => {
      if (u.last_login_at) {
        const loginDate = new Date(u.last_login_at);
        if (loginDate >= today) activeTodayCount++;
        if (loginDate >= lastWeek) activeThisWeekCount++;
      }
    });

    this.stats.activeToday = activeTodayCount;
    this.stats.activeThisWeek = activeThisWeekCount;
  }

  openUserDetails(user: User) {
    this.dialog.open(UserDetailsDialogComponent, {
      width: '600px',
      maxWidth: '90vw',
      data: user,
      autoFocus: false
    });
  }
}
