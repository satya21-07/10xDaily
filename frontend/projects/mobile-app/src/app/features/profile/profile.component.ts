import { Component, OnInit, inject, NgZone } from '@angular/core';
import { CommonModule } from '@angular/common';
import { IonicModule } from '@ionic/angular';
import { FormsModule } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { AuthService, UserProfile } from '../../services/auth.service';
import { ProgressService } from '../../services/progress.service';
import { ThemeService, AppTheme } from '../../services/theme.service';
import { addIcons } from 'ionicons';
import { ToastController, ActionSheetController } from '@ionic/angular';
import { 
  logOutOutline, settingsOutline, notificationsOutline, moonOutline,
  flame, gridOutline, bulbOutline, checkmarkCircle, pencilOutline, logoGoogle,
  bookOutline, locateOutline, starOutline, timeOutline, book, newspaperOutline,
  locate, chatboxEllipsesOutline, personOutline, shieldCheckmarkOutline,
  colorPaletteOutline, globeOutline, helpCircleOutline, chevronForwardOutline,
  ribbon, sunnyOutline, phonePortraitOutline
} from 'ionicons/icons';

@Component({
  selector: 'app-profile',
  standalone: true,
  imports: [CommonModule, IonicModule, FormsModule, RouterModule],
  templateUrl: './profile.component.html',
  styleUrls: ['./profile.component.scss']
})
export class ProfileComponent implements OnInit {
  private authService = inject(AuthService);
  private router = inject(Router);
  private ngZone = inject(NgZone);
  private toastController = inject(ToastController);
  private actionSheetCtrl = inject(ActionSheetController);
  public progressService = inject(ProgressService);
  public themeService = inject(ThemeService);
  
  user: UserProfile | null = null;

  // Settings state
  pushEnabled = true;

  constructor() {
    addIcons({
      logOutOutline, settingsOutline, notificationsOutline, moonOutline,
      flame, gridOutline, bulbOutline, checkmarkCircle, pencilOutline, logoGoogle,
      bookOutline, locateOutline, starOutline, timeOutline, book, newspaperOutline,
      locate, chatboxEllipsesOutline, personOutline, shieldCheckmarkOutline,
      colorPaletteOutline, globeOutline, helpCircleOutline, chevronForwardOutline,
      ribbon, sunnyOutline, phonePortraitOutline
    });
  }

  ngOnInit() {
    this.authService.currentUser$.subscribe(user => {
      if (!user) {
        // Ionic tabs bug: CanActivate guards break the tab state machine.
        // We handle the auth redirect manually here instead.
        this.ngZone.run(() => {
          this.router.navigate(['/login'], { replaceUrl: true });
        });
      } else {
        this.user = user;
      }
    });
  }

  ionViewWillEnter() {
    // Fetch fresh stats from backend every time the tab is opened
    if (this.authService.isLoggedIn) {
      this.authService.fetchProfile().subscribe();
    }
  }

  onLogout() {
    this.authService.logout();
    this.ngZone.run(() => {
      this.router.navigate(['/login']);
    });
  }
  
  async showFeatureNotAvailable(featureName: string) {
    const toast = await this.toastController.create({
      message: `${featureName} is coming soon!`,
      duration: 2000,
      position: 'bottom',
      color: 'dark'
    });
    await toast.present();
  }

  async openThemeActionSheet() {
    const actionSheet = await this.actionSheetCtrl.create({
      header: 'Choose Theme',
      cssClass: 'compact-action-sheet',
      buttons: [
        {
          text: 'Light',
          icon: 'sunny-outline',
          handler: () => {
            this.themeService.setTheme('light');
          }
        },
        {
          text: 'Dark',
          icon: 'moon-outline',
          handler: () => {
            this.themeService.setTheme('dark');
          }
        },
        {
          text: 'System Default',
          icon: 'phone-portrait-outline',
          handler: () => {
            this.themeService.setTheme('system');
          }
        },
        {
          text: 'Cancel',
          role: 'cancel'
        }
      ]
    });
    await actionSheet.present();
  }

  // Dynamic Stat Getters
  get wordsLearned(): number {
    return this.user?.words_learned || 0;
  }
  
  get quizAccuracy(): string {
    const correct = this.user?.quiz_correct_answers || 0;
    const total = this.user?.quiz_total_answers || 0;
    if (total === 0) return '0%';
    return Math.round((correct / total) * 100) + '%';
  }
  
  get totalXp(): number {
    const modules = this.user?.modules_completed || 0;
    return (this.user?.streak || 0) * 10 + (modules * 100); // Also include streak in XP just to make it cool, or just modules
  }
  
  get timeLearned(): string {
    const totalSecs = this.user?.total_time_spent_seconds || 0;
    if (totalSecs < 60) return '< 1m';
    
    const hrs = Math.floor(totalSecs / 3600);
    const mins = Math.floor((totalSecs % 3600) / 60);
    
    if (hrs > 0) return `${hrs}h ${mins}m`;
    return `${mins}m`;
  }

  onFileSelected(event: any) {
    const file = event.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e: any) => {
        if (this.user) {
          const base64Image = e.target.result;
          this.user.avatarUrl = base64Image;
          this.authService.updateAvatar(base64Image).subscribe();
        }
      };
      reader.readAsDataURL(file);
    }
  }
}
