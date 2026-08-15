import { Component, inject, OnInit } from '@angular/core';
import { CommonModule, Location } from '@angular/common';
import { IonicModule } from '@ionic/angular';
import { RouterModule } from '@angular/router';
import { GamesService } from '../../../services/games.service';
import { AuthService, UserProfile } from '../../../services/auth.service';
import { addIcons } from 'ionicons';
import { colorFilter, checkmarkCircle, sparkles, arrowForward, grid, text, menuOutline, addCircle, calendarOutline, trophy, timerOutline, bookmarkOutline, personOutline, homeOutline, gameControllerOutline, arrowBackOutline } from 'ionicons/icons';

@Component({
  selector: 'app-games-hub',
  standalone: true,
  imports: [CommonModule, IonicModule, RouterModule],
  templateUrl: './games-hub.component.html',
  styleUrls: ['./games-hub.component.scss']
})
export class GamesHubComponent implements OnInit {
  private gamesService = inject(GamesService);
  private authService = inject(AuthService);
  private location = inject(Location);
  
  userProfile: UserProfile | null = null;
  
  constructor() {
    addIcons({ colorFilter, checkmarkCircle, sparkles, arrowForward, grid, text, menuOutline, addCircle, calendarOutline, trophy, timerOutline, bookmarkOutline, personOutline, homeOutline, gameControllerOutline, arrowBackOutline });
  }
  
  flowCompleted = false;
  flowStreak = 0;
  flowTime = '--:--';
  
  wordSearchCompleted = false;
  wordSearchStreak = 0;
  wordSearchTime = '--:--';
  
  miniSudokuCompleted = false;
  miniSudokuStreak = 0;
  miniSudokuTime = '--:--';

  ngOnInit() {
    this.authService.currentUser$.subscribe(profile => {
      this.userProfile = profile;
    });

    this.gamesService.getTodayFlowPuzzle().subscribe(res => {
      this.flowCompleted = res.completed;
      this.flowStreak = res.game_streak || 0;
      if (res.completed && res.time_taken) {
        this.flowTime = this.formatTime(res.time_taken);
      }
    });
    
    this.gamesService.getTodayWordSearch().subscribe(res => {
      this.wordSearchCompleted = res.completed;
      this.wordSearchStreak = res.game_streak || 0;
      if (res.completed && res.saved_state && res.saved_state.time_taken) {
        this.wordSearchTime = this.formatTime(res.saved_state.time_taken);
      }
    });
    
    this.gamesService.getTodayMiniSudoku().subscribe(res => {
      this.miniSudokuCompleted = res.completed;
      this.miniSudokuStreak = res.game_streak || 0;
      if (res.completed && res.saved_state && res.saved_state.time_taken) {
        this.miniSudokuTime = this.formatTime(res.saved_state.time_taken);
      }
    });
  }

  formatTime(seconds: number): string {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  }

  goBack() {
    this.location.back();
  }
}
