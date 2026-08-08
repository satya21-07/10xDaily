import { Component, inject, OnInit, OnDestroy } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { IonicModule } from '@ionic/angular';
import { ThemeService } from './services/theme.service';
import { AuthService } from './services/auth.service';

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
  
  private timeTrackerInterval: any;

  ngOnInit() {
    // Track time spent in app (every 60 seconds)
    this.timeTrackerInterval = setInterval(() => {
      if (this.authService.isLoggedIn) {
        this.authService.updateStats({ time_spent_increment_seconds: 60 }).subscribe();
      }
    }, 60000);
  }
  
  ngOnDestroy() {
    if (this.timeTrackerInterval) {
      clearInterval(this.timeTrackerInterval);
    }
  }
}
