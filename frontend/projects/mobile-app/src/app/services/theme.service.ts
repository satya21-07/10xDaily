import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ThemeService {
  private readonly THEME_KEY = '10xdaily_dark_mode';
  private isDarkSubject = new BehaviorSubject<boolean>(false);
  
  isDark$ = this.isDarkSubject.asObservable();

  constructor() {
    this.initTheme();
  }

  private initTheme() {
    if (typeof window !== 'undefined') {
      const stored = localStorage.getItem(this.THEME_KEY);
      if (stored !== null) {
        this.setDark(stored === 'true');
      } else {
        // Check system preference
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        this.setDark(prefersDark);
      }
    }
  }

  setDark(isDark: boolean) {
    this.isDarkSubject.next(isDark);
    if (typeof window !== 'undefined') {
      localStorage.setItem(this.THEME_KEY, String(isDark));
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

  toggle() {
    this.setDark(!this.isDarkSubject.value);
  }
}
