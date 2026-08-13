import { Component, inject, OnInit, OnDestroy, HostListener } from '@angular/core';
import { RouterOutlet, Router } from '@angular/router';
import { IonicModule } from '@ionic/angular';
import { ThemeService } from './services/theme.service';
import { AuthService } from './services/auth.service';
import { Subscription } from 'rxjs';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, IonicModule],
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss'
})
export class AppComponent implements OnInit, OnDestroy {
  title = 'mobile-app';
  private themeService = inject(ThemeService);
  private authService = inject(AuthService);
  private router = inject(Router);
  
  private timeTrackerInterval: any;
  private inactivityTimeout: any;
  private readonly INACTIVITY_TIME_LIMIT = 15 * 60 * 1000; // 15 minutes
  private authSubscription: Subscription | undefined;

  ngOnInit() {
    // Sync profile on app load if logged in
    if (this.authService.isLoggedIn) {
      this.authService.fetchProfile().subscribe();
    }

    this.authSubscription = this.authService.currentUser$.subscribe(user => {
      if (user) {
        this.startInactivityTimer();
      } else {
        this.clearInactivityTimer();
      }
    });

    // Track time spent in app (every 60 seconds)
    this.timeTrackerInterval = setInterval(() => {
      if (this.authService.isLoggedIn) {
        this.authService.updateStats({ time_spent_increment_seconds: 60 }).subscribe();
      }
    }, 60000);
  }

  @HostListener('window:mousemove')
  @HostListener('window:keydown')
  @HostListener('window:click')
  @HostListener('window:touchstart')
  @HostListener('window:scroll')
  resetInactivityTimer() {
    if (this.authService.isLoggedIn) {
      this.startInactivityTimer();
    }
  }

  private startInactivityTimer() {
    this.clearInactivityTimer();
    
    // Only run the timer if the user is logged in
    if (!this.authService.isLoggedIn) return;

    this.inactivityTimeout = setTimeout(() => {
      this.authService.logout();
      this.router.navigate(['/login']);
    }, this.INACTIVITY_TIME_LIMIT);
  }

  private clearInactivityTimer() {
    if (this.inactivityTimeout) {
      clearTimeout(this.inactivityTimeout);
      this.inactivityTimeout = null;
    }
  }
  
  ngOnDestroy() {
    if (this.timeTrackerInterval) {
      clearInterval(this.timeTrackerInterval);
    }
    this.clearInactivityTimer();
    if (this.authSubscription) {
      this.authSubscription.unsubscribe();
    }
  }
}
