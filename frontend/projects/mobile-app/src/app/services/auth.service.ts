import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { BehaviorSubject, Observable, tap, catchError, of, throwError } from 'rxjs';
import { environment } from '../../environments/environment';

export interface UserProfile {
  id?: number;
  name: string;
  email: string;
  phoneNumber?: string;
  dateOfBirth?: string;
  avatarUrl: string;
  streak: number;
  modulesExplored: number;
  aiInsights: number;
  joinDate: string;
  words_learned?: number;
  quiz_correct_answers?: number;
  quiz_total_answers?: number;
  modules_completed?: number;
  total_time_spent_seconds?: number;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: {
    id: number;
    email: string;
    full_name: string;
    phone_number?: string;
    date_of_birth?: string;
    streak?: number;
    words_learned?: number;
    quiz_correct_answers?: number;
    quiz_total_answers?: number;
    modules_completed?: number;
    total_time_spent_seconds?: number;
    avatar?: string;
  };
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private readonly AUTH_KEY = '10xdaily_auth_state';
  private readonly TOKEN_KEY = '10xdaily_access_token';
  
  private http = inject(HttpClient);
  private apiUrl = environment.apiUrl || 'http://localhost:8000/api/v1';

  private currentUserSubject = new BehaviorSubject<UserProfile | null>(null);

  constructor() {
    this.loadInitialState();
  }

  private loadInitialState(): void {
    if (typeof window !== 'undefined' && window.localStorage) {
      const storedState = localStorage.getItem(this.AUTH_KEY);
      if (storedState) {
        try {
          const user = JSON.parse(storedState);
          this.currentUserSubject.next(user);
        } catch (e) {
          console.error('Failed to parse auth state', e);
          this.logout();
        }
      }
    }
  }

  get currentUser$(): Observable<UserProfile | null> {
    return this.currentUserSubject.asObservable();
  }

  get currentUserValue(): UserProfile | null {
    return this.currentUserSubject.value;
  }

  get isLoggedIn(): boolean {
    return !!this.currentUserValue;
  }

  getToken(): string | null {
    if (typeof window !== 'undefined' && window.localStorage) {
      return localStorage.getItem(this.TOKEN_KEY);
    }
    return null;
  }

  register(email: string, password: string, name: string): Observable<AuthResponse> {
    return this.http.post<AuthResponse>(`${this.apiUrl}/auth/register`, {
      email, password, full_name: name
    }).pipe(
      tap(res => this.handleAuthResponse(res))
    );
  }

  updateStats(increments: {
    words_learned_increment?: number;
    quiz_correct_increment?: number;
    quiz_total_increment?: number;
    modules_completed_increment?: number;
    time_spent_increment_seconds?: number;
  }): Observable<any> {
    console.log('[AuthService] Attempting to update stats:', increments);
    if (!this.isLoggedIn) {
      console.warn('[AuthService] Aborted stats update because user is not logged in!');
      return of(null);
    }
    
    const headers = new HttpHeaders({
      'Authorization': `Bearer ${this.getToken()}`
    });
    
    return this.http.patch(`${this.apiUrl}/users/me/stats`, increments, { headers }).pipe(
      tap((updatedUser: any) => {
        console.log('[AuthService] Successfully updated stats on backend!', updatedUser);
        // Sync local profile state
        const current = this.currentUserSubject.value;
        if (current) {
          const newProfile = {
            ...current,
            streak: updatedUser.current_streak || current.streak,
            words_learned: updatedUser.words_learned,
            quiz_correct_answers: updatedUser.quiz_correct_answers,
            quiz_total_answers: updatedUser.quiz_total_answers,
            modules_completed: updatedUser.modules_completed,
            total_time_spent_seconds: updatedUser.total_time_spent_seconds
          };
          this.currentUserSubject.next(newProfile);
          if (typeof window !== 'undefined' && window.localStorage) {
            localStorage.setItem(this.AUTH_KEY, JSON.stringify(newProfile));
          }
        }
      }),
      catchError(err => {
        console.error('Failed to sync stats', err);
        return of(null);
      })
    );
  }

  fetchProfile(): Observable<any> {
    if (!this.isLoggedIn) return of(null);
    
    const headers = new HttpHeaders({
      'Authorization': `Bearer ${this.getToken()}`
    });
    
    return this.http.get(`${this.apiUrl}/users/me`, { headers }).pipe(
      tap((updatedUser: any) => {
        const current = this.currentUserSubject.value;
        if (current) {
          const newProfile = {
            ...current,
            streak: updatedUser.current_streak,
            words_learned: updatedUser.words_learned,
            quiz_correct_answers: updatedUser.quiz_correct_answers,
            quiz_total_answers: updatedUser.quiz_total_answers,
            modules_completed: updatedUser.modules_completed,
            total_time_spent_seconds: updatedUser.total_time_spent_seconds,
            phoneNumber: updatedUser.phone_number,
            dateOfBirth: updatedUser.date_of_birth
          };
          if (updatedUser.avatar) {
            newProfile.avatarUrl = updatedUser.avatar;
          }
          this.currentUserSubject.next(newProfile);
          if (typeof window !== 'undefined' && window.localStorage) {
            localStorage.setItem(this.AUTH_KEY, JSON.stringify(newProfile));
          }
        }
      }),
      catchError(err => {
        console.error('Failed to fetch profile', err);
        return of(null);
      })
    );
  }

  login(email: string, password: string): Observable<AuthResponse> {
    const body = new URLSearchParams();
    body.set('username', email);
    body.set('password', password);

    const headers = new HttpHeaders({
      'Content-Type': 'application/x-www-form-urlencoded'
    });

    return this.http.post<AuthResponse>(`${this.apiUrl}/auth/login/access-token`, body.toString(), { headers }).pipe(
      tap(res => this.handleAuthResponse(res))
    );
  }

  loginWithGoogle(token: string): Observable<AuthResponse> {
    return this.http.post<AuthResponse>(`${this.apiUrl}/auth/google`, { token }).pipe(
      tap(res => this.handleAuthResponse(res))
    );
  }

  private handleAuthResponse(res: AuthResponse): void {
    const profile: UserProfile = {
      id: res.user.id,
      name: res.user.full_name,
      email: res.user.email,
      phoneNumber: res.user.phone_number,
      dateOfBirth: res.user.date_of_birth,
      avatarUrl: res.user.avatar || `https://api.dicebear.com/7.x/avataaars/svg?seed=${res.user.email}`,
      streak: res.user.streak || 1,
      modulesExplored: 0,
      aiInsights: 0,
      joinDate: new Date().toISOString(),
      words_learned: res.user.words_learned || 0,
      quiz_correct_answers: res.user.quiz_correct_answers || 0,
      quiz_total_answers: res.user.quiz_total_answers || 0,
      modules_completed: res.user.modules_completed || 0,
      total_time_spent_seconds: res.user.total_time_spent_seconds || 0
    };
    
    if (typeof window !== 'undefined' && window.localStorage) {
      localStorage.setItem(this.AUTH_KEY, JSON.stringify(profile));
      localStorage.setItem(this.TOKEN_KEY, res.access_token);
    }
    this.currentUserSubject.next(profile);
  }

  logout(): void {
    if (typeof window !== 'undefined' && window.localStorage) {
      // Preserve theme preference across logouts
      const themePref = localStorage.getItem('10xdaily_dark_mode');
      
      localStorage.clear();
      
      if (themePref !== null) {
        localStorage.setItem('10xdaily_dark_mode', themePref);
      }
    }
    this.currentUserSubject.next(null);
  }

  updateLocalProfile(profile: UserProfile): void {
    this.currentUserSubject.next(profile);
    if (typeof window !== 'undefined' && window.localStorage) {
      localStorage.setItem(this.AUTH_KEY, JSON.stringify(profile));
    }
  }

  updateAvatar(base64Image: string): Observable<any> {
    if (!this.isLoggedIn) return of(null);
    
    const headers = new HttpHeaders({
      'Authorization': `Bearer ${this.getToken()}`
    });
    
    return this.http.patch(`${this.apiUrl}/users/me/avatar`, { avatar: base64Image }, { headers }).pipe(
      tap(() => {
        const current = this.currentUserSubject.value;
        if (current) {
          current.avatarUrl = base64Image;
          this.updateLocalProfile(current);
        }
      }),
      catchError(err => {
        console.error('Failed to update avatar on backend', err);
        return of(null);
      })
    );
  }

  updateProfile(data: { full_name?: string, phone_number?: string, date_of_birth?: string }): Observable<any> {
    if (!this.isLoggedIn) return of(null);
    
    const headers = new HttpHeaders({
      'Authorization': `Bearer ${this.getToken()}`
    });
    
    return this.http.patch(`${this.apiUrl}/users/me/profile`, data, { headers }).pipe(
      tap((updatedUser: any) => {
        const current = this.currentUserSubject.value;
        if (current) {
          const newProfile = {
            ...current,
            name: updatedUser.full_name,
            phoneNumber: updatedUser.phone_number,
            dateOfBirth: updatedUser.date_of_birth
          };
          this.updateLocalProfile(newProfile);
        }
      }),
      catchError(err => {
        console.error('Failed to update profile on backend', err);
        return throwError(() => err);
      })
    );
  }

  deleteAccount(): Observable<any> {
    if (!this.isLoggedIn) return of(null);
    
    const headers = new HttpHeaders({
      'Authorization': `Bearer ${this.getToken()}`
    });
    
    return this.http.delete(`${this.apiUrl}/users/me`, { headers }).pipe(
      tap(() => {
        this.logout();
      }),
      catchError(err => {
        console.error('Failed to delete account', err);
        return throwError(() => err);
      })
    );
  }
}
