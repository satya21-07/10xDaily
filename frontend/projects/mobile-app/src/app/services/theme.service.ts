import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

export type AppTheme = 'light' | 'dark' | 'system';

@Injectable({
  providedIn: 'root'
})
export class ThemeService {
  public readonly THEME_KEY = '10xdaily_theme_pref';
  
  private isDarkSubject = new BehaviorSubject<boolean>(false);
  isDark$ = this.isDarkSubject.asObservable();
  
  private currentThemeSubject = new BehaviorSubject<AppTheme>('system');
  currentTheme$ = this.currentThemeSubject.asObservable();

  constructor() {
    this.initTheme();
  }

  private initTheme() {
    if (typeof window !== 'undefined') {
      const stored = localStorage.getItem(this.THEME_KEY) as AppTheme | null;
      const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
      
      if (stored === 'light' || stored === 'dark') {
        this.currentThemeSubject.next(stored);
        this.applyTheme(stored === 'dark');
      } else {
        this.currentThemeSubject.next('system');
        this.applyTheme(mediaQuery.matches);
      }

      mediaQuery.addEventListener('change', (e) => {
        if (this.currentThemeSubject.value === 'system') {
          this.applyTheme(e.matches);
        }
      });
    }
  }

  setTheme(theme: AppTheme) {
    this.currentThemeSubject.next(theme);
    
    if (typeof window !== 'undefined') {
      if (theme === 'system') {
        localStorage.removeItem(this.THEME_KEY);
        const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
        this.applyTheme(mediaQuery.matches);
      } else {
        localStorage.setItem(this.THEME_KEY, theme);
        this.applyTheme(theme === 'dark');
      }
    }
  }

  private applyTheme(isDark: boolean) {
    this.isDarkSubject.next(isDark);
    if (typeof window !== 'undefined') {
      if (isDark) {
        document.body.classList.add('dark-theme');
        document.body.classList.remove('light-theme');
        document.documentElement.classList.add('ion-palette-dark');
      } else {
        document.body.classList.add('light-theme');
        document.body.classList.remove('dark-theme');
        document.documentElement.classList.remove('ion-palette-dark');
      }
    }
  }
}
