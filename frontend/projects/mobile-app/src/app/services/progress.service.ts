import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { BehaviorSubject, Observable, catchError, of } from 'rxjs';
import { AuthService } from './auth.service';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class ProgressService {
  private visitedModulesSubject = new BehaviorSubject<Set<string>>(new Set());
  private authService = inject(AuthService);
  private http = inject(HttpClient);
  private apiUrl = environment.apiUrl || 'http://localhost:8000/api/v1';
  private currentUserId: number | null = null;
  
  constructor() {
    this.authService.currentUser$.subscribe(user => {
      this.currentUserId = user ? user.id || null : null;
      this.loadState();
    });
  }
  
  private getTodayKey(): string {
    const today = new Date();
    const userIdPrefix = this.currentUserId ? `${this.currentUserId}_` : '';
    return `10xdaily_progress_${userIdPrefix}${today.getFullYear()}-${(today.getMonth() + 1).toString().padStart(2, '0')}-${today.getDate().toString().padStart(2, '0')}`;
  }

  private loadState() {
    if (this.currentUserId !== null) {
      if (this.authService.isLoggedIn) {
        const headers = new HttpHeaders({
          'Authorization': `Bearer ${this.authService.getToken()}`
        });
        this.http.get<{visited_modules: string[]}>(`${this.apiUrl}/users/me/progress/modules`, { headers }).pipe(
          catchError(() => {
            this.loadStateFromStorage();
            return of({visited_modules: []});
          })
        ).subscribe(res => {
          if (res && res.visited_modules && res.visited_modules.length > 0) {
            this.visitedModulesSubject.next(new Set(res.visited_modules));
          } else {
            this.loadStateFromStorage();
          }
        });
      } else {
        this.loadStateFromStorage();
      }
    } else {
      this.visitedModulesSubject.next(new Set());
    }
  }
  
  private loadStateFromStorage() {
    if (typeof window !== 'undefined' && window.localStorage && this.currentUserId !== null) {
      const todayKey = this.getTodayKey();
      const stored = localStorage.getItem(todayKey);
      if (stored) {
        try {
          const arr = JSON.parse(stored);
          this.visitedModulesSubject.next(new Set(arr));
        } catch(e) {
          console.error("Failed to parse progress", e);
        }
      } else {
        this.visitedModulesSubject.next(new Set());
      }
    } else {
      this.visitedModulesSubject.next(new Set());
    }
  }
  
  private saveState(modules: Set<string>) {
    if (typeof window !== 'undefined' && window.localStorage && this.currentUserId !== null) {
      const todayKey = this.getTodayKey();
      localStorage.setItem(todayKey, JSON.stringify(Array.from(modules)));
    }
    
    if (this.authService.isLoggedIn) {
      const headers = new HttpHeaders({
        'Authorization': `Bearer ${this.authService.getToken()}`
      });
      this.http.post(`${this.apiUrl}/users/me/progress/modules`, { visited_modules: Array.from(modules) }, { headers })
        .subscribe({
          error: (err) => console.error('Failed to sync modules progress', err)
        });
    }
  }

  markVisited(moduleId: string) {
    if (this.currentUserId === null) return;
    
    const currentSet = this.visitedModulesSubject.value;
    if (!currentSet.has(moduleId)) {
      currentSet.add(moduleId);
      this.saveState(currentSet);
      this.visitedModulesSubject.next(new Set(currentSet));
    }
  }

  get exploredCount$(): Observable<number> {
    return new Observable<number>(observer => {
      return this.visitedModulesSubject.subscribe(set => {
        observer.next(set.size);
      });
    });
  }
  
  get currentExploredCount(): number {
    return this.visitedModulesSubject.value.size;
  }
}
