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
  private completedHabitsSubject = new BehaviorSubject<Set<string>>(new Set());
  private authService = inject(AuthService);
  private http = inject(HttpClient);
  private apiUrl = environment.apiUrl || 'http://localhost:8000/api/v1';
  private currentUserId: number | null = null;
  
  constructor() {
    this.authService.currentUser$.subscribe(user => {
      this.currentUserId = user ? user.id || null : null;
      this.loadState();
      this.loadHabitState();
    });
  }
  
  private getTodayKey(): string {
    const today = new Date();
    const userIdPrefix = this.currentUserId ? `${this.currentUserId}_` : '';
    return `10xdaily_progress_${userIdPrefix}${today.getFullYear()}-${(today.getMonth() + 1).toString().padStart(2, '0')}-${today.getDate().toString().padStart(2, '0')}`;
  }

  private getTodayHabitsKey(): string {
    const today = new Date();
    const userIdPrefix = this.currentUserId ? `${this.currentUserId}_` : '';
    return `10xdaily_habits_${userIdPrefix}${today.getFullYear()}-${(today.getMonth() + 1).toString().padStart(2, '0')}-${today.getDate().toString().padStart(2, '0')}`;
  }

  private loadState() {
    if (this.currentUserId !== null) {
      // Optimistically load from storage first to provide instant UI
      this.loadStateFromStorage();

      if (this.authService.isLoggedIn) {
        const headers = new HttpHeaders({
          'Authorization': `Bearer ${this.authService.getToken()}`
        });
        this.http.get<{visited_modules: string[]}>(`${this.apiUrl}/users/me/progress/modules`, { headers }).pipe(
          catchError(() => {
            return of({visited_modules: []});
          })
        ).subscribe(res => {
          if (res && res.visited_modules && res.visited_modules.length > 0) {
            const current = this.visitedModulesSubject.value;
            const backendSet = new Set(res.visited_modules);
            // Merge both to prevent overriding local optimistic updates that might have happened during request
            const merged = new Set([...Array.from(current), ...Array.from(backendSet)]);
            this.visitedModulesSubject.next(merged);
            this.saveStateLocallyOnly(merged);
          }
        });
      }
    } else {
      this.visitedModulesSubject.next(new Set());
    }
  }
  
  private saveStateLocallyOnly(modules: Set<string>) {
    if (typeof window !== 'undefined' && window.localStorage && this.currentUserId !== null) {
      const todayKey = this.getTodayKey();
      localStorage.setItem(todayKey, JSON.stringify(Array.from(modules)));
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
      
      // Increment all-time modules_explored tracker
      if (this.authService.isLoggedIn) {
        this.authService.updateStats({ modules_explored_increment: 1 }).subscribe();
      }
    }
  }

  get exploredCount$(): Observable<number> {
    return new Observable<number>(observer => {
      return this.visitedModulesSubject.subscribe(set => {
        observer.next(set.size);
      });
    });
  }
  
  get visitedModules$(): Observable<Set<string>> {
    return this.visitedModulesSubject.asObservable();
  }
  
  get currentExploredCount(): number {
    return this.visitedModulesSubject.value.size;
  }

  // --- Habits Progress ---
  private loadHabitState() {
    if (this.currentUserId !== null) {
      // Optimistically load from storage first
      this.loadHabitStateFromStorage();

      if (this.authService.isLoggedIn) {
        const headers = new HttpHeaders({
          'Authorization': `Bearer ${this.authService.getToken()}`
        });
        this.http.get<{completed_habits: string[]}>(`${this.apiUrl}/users/me/progress/habits`, { headers }).pipe(
          catchError(() => {
            return of({completed_habits: []});
          })
        ).subscribe(res => {
          if (res && res.completed_habits && res.completed_habits.length > 0) {
            const current = this.completedHabitsSubject.value;
            const backendSet = new Set(res.completed_habits);
            const merged = new Set([...Array.from(current), ...Array.from(backendSet)]);
            this.completedHabitsSubject.next(merged);
            this.saveHabitStateLocallyOnly(merged);
          }
        });
      }
    } else {
      this.completedHabitsSubject.next(new Set());
    }
  }

  private saveHabitStateLocallyOnly(habits: Set<string>) {
    if (typeof window !== 'undefined' && window.localStorage && this.currentUserId !== null) {
      const todayKey = this.getTodayHabitsKey();
      localStorage.setItem(todayKey, JSON.stringify(Array.from(habits)));
    }
  }

  private loadHabitStateFromStorage() {
    if (typeof window !== 'undefined' && window.localStorage && this.currentUserId !== null) {
      const todayKey = this.getTodayHabitsKey();
      const stored = localStorage.getItem(todayKey);
      if (stored) {
        try {
          const arr = JSON.parse(stored);
          this.completedHabitsSubject.next(new Set(arr));
        } catch(e) {
          console.error("Failed to parse habits", e);
        }
      } else {
        this.completedHabitsSubject.next(new Set());
      }
    } else {
      this.completedHabitsSubject.next(new Set());
    }
  }

  private saveHabitState(habits: Set<string>) {
    if (typeof window !== 'undefined' && window.localStorage && this.currentUserId !== null) {
      const todayKey = this.getTodayHabitsKey();
      localStorage.setItem(todayKey, JSON.stringify(Array.from(habits)));
    }
    
    if (this.authService.isLoggedIn) {
      const headers = new HttpHeaders({
        'Authorization': `Bearer ${this.authService.getToken()}`
      });
      this.http.post(`${this.apiUrl}/users/me/progress/habits`, { completed_habits: Array.from(habits) }, { headers })
        .subscribe({
          error: (err) => console.error('Failed to sync habits progress', err)
        });
    }
  }

  toggleHabit(habitTitle: string) {
    if (this.currentUserId === null) return;
    const currentSet = this.completedHabitsSubject.value;
    if (currentSet.has(habitTitle)) {
      currentSet.delete(habitTitle);
    } else {
      currentSet.add(habitTitle);
    }
    this.saveHabitState(currentSet);
    this.completedHabitsSubject.next(new Set(currentSet));
  }

  isHabitCompleted(habitTitle: string): boolean {
    return this.completedHabitsSubject.value.has(habitTitle);
  }
}
