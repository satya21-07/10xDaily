import { Injectable, inject } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';
import { AuthService } from './auth.service';

@Injectable({
  providedIn: 'root'
})
export class ProgressService {
  private visitedModulesSubject = new BehaviorSubject<Set<string>>(new Set());
  private authService = inject(AuthService);
  private currentUserId: number | null = null;
  
  constructor() {
    this.authService.currentUser$.subscribe(user => {
      this.currentUserId = user ? user.id || null : null;
      this.loadState();
    });
  }
  
  private getTodayKey(): string {
    const today = new Date();
    // Use local date string YYYY-MM-DD and append user ID
    const userIdPrefix = this.currentUserId ? `${this.currentUserId}_` : '';
    return `10xdaily_progress_${userIdPrefix}${today.getFullYear()}-${(today.getMonth() + 1).toString().padStart(2, '0')}-${today.getDate().toString().padStart(2, '0')}`;
  }

  private loadState() {
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
  }

  /**
   * Mark a module as visited for today
   */
  markVisited(moduleId: string) {
    if (this.currentUserId === null) return;
    
    const currentSet = this.visitedModulesSubject.value;
    if (!currentSet.has(moduleId)) {
      currentSet.add(moduleId);
      this.saveState(currentSet);
      this.visitedModulesSubject.next(new Set(currentSet));
    }
  }

  /**
   * Get an observable of the count of visited modules
   */
  get exploredCount$(): Observable<number> {
    return new Observable<number>(observer => {
      return this.visitedModulesSubject.subscribe(set => {
        observer.next(set.size);
      });
    });
  }
  
  /**
   * Get the current count synchronously
   */
  get currentExploredCount(): number {
    return this.visitedModulesSubject.value.size;
  }
}
