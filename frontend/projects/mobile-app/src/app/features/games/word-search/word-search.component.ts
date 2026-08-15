import { Component, ElementRef, HostListener, OnInit, inject } from '@angular/core';
import { CommonModule, Location } from '@angular/common';
import { IonicModule, ToastController } from '@ionic/angular';
import { GamesService, WordSearchLevel, TodayWordSearchResponse } from '../../../services/games.service';
import { AuthService } from '../../../services/auth.service';
import { addIcons } from 'ionicons';
import { refresh, checkmarkCircle, bulb } from 'ionicons/icons';

interface GridCell {
  x: number;
  y: number;
  letter: string;
  isSelected: boolean;
  isFound: boolean;
  isHinted?: boolean;
  color?: string; // Color assigned when a word is found
}

@Component({
  selector: 'app-word-search',
  standalone: true,
  imports: [CommonModule, IonicModule],
  templateUrl: './word-search.component.html',
  styleUrls: ['./word-search.component.scss']
})
export class WordSearchComponent implements OnInit {
  private gamesService = inject(GamesService);
  private authService = inject(AuthService);
  private location = inject(Location);
  private toastCtrl = inject(ToastController);

  levelData: WordSearchLevel | null = null;
  grid: GridCell[][] = [];
  gridSize = 10;
  
  foundWords: string[] = [];
  targetWords: string[] = [];
  
  // Hint state
  currentHint: { word: string, length: number } | null = null;
  
  // Timer state
  timer: number = 0;
  timerInterval: any;
  timerFormatted: string = '00:00';
  
  isCompleted = false;
  alreadyCompletedToday = false;
  savedState: any = null;

  // Selection state
  isSelecting = false;
  startCell: GridCell | null = null;
  currentSelection: GridCell[] = [];
  
  colors = ['#ef4444', '#3b82f6', '#22c55e', '#eab308', '#f97316', '#a855f7', '#06b6d4', '#ec4899', '#84cc16', '#14b8a6'];

  constructor() {
    addIcons({ refresh, checkmarkCircle, bulb });
  }

  ngOnInit() {
    this.gamesService.getTodayWordSearch().subscribe(res => {
      this.alreadyCompletedToday = res.completed;
      this.levelData = res.level;
      this.savedState = res.saved_state;
      this.initGame();
    });
  }

  initGame() {
    if (!this.levelData) return;
    
    this.targetWords = this.levelData.words;
    this.foundWords = [];
    this.timer = 0;
    this.updateTimerDisplay();
    this.isCompleted = false;
    
    // Initialize Grid
    this.grid = [];
    for (let y = 0; y < this.gridSize; y++) {
      const row: GridCell[] = [];
      for (let x = 0; x < this.gridSize; x++) {
        row.push({
          x, y,
          letter: this.levelData.grid[y][x],
          isSelected: false,
          isFound: false
        });
      }
      this.grid.push(row);
    }
    
    // Load saved state
    if (this.savedState) {
      this.foundWords = this.savedState.found_words || [];
      this.timer = this.savedState.time_taken || 0;
      this.updateTimerDisplay();
      
      // Apply found styling
      this.foundWords.forEach((word, index) => {
        const sol = this.levelData!.solution.find(s => s.word === word);
        if (sol) {
          const color = this.colors[index % this.colors.length];
          this.colorWord(sol.start[0], sol.start[1], sol.end[0], sol.end[1], color);
        }
      });
      
      if (this.alreadyCompletedToday || this.foundWords.length === this.targetWords.length) {
        this.isCompleted = true;
      } else {
        this.startTimer();
      }
    } else {
      if (this.alreadyCompletedToday) {
        this.isCompleted = true;
      } else {
        this.startTimer();
      }
    }
  }

  colorWord(sx: number, sy: number, ex: number, ey: number, color: string) {
    const dx = Math.sign(ex - sx);
    const dy = Math.sign(ey - sy);
    const length = Math.max(Math.abs(ex - sx), Math.abs(ey - sy)) + 1;
    
    for (let i = 0; i < length; i++) {
      const cell = this.grid[sy + dy * i][sx + dx * i];
      cell.isFound = true;
      cell.color = color;
    }
  }

  startTimer() {
    if (this.timerInterval) clearInterval(this.timerInterval);
    this.timerInterval = setInterval(() => {
      this.timer++;
      this.updateTimerDisplay();
    }, 1000);
  }

  stopTimer() {
    if (this.timerInterval) {
      clearInterval(this.timerInterval);
      this.timerInterval = null;
    }
  }

  updateTimerDisplay() {
    const mins = Math.floor(this.timer / 60);
    const secs = this.timer % 60;
    this.timerFormatted = `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  }

  goBack() {
    this.location.back();
  }

  reset() {
    this.stopTimer();
    this.savedState = null;
    this.currentHint = null;
    this.initGame();
  }

  showHint() {
    if (this.isCompleted || !this.levelData) return;
    
    // Pick an unfound word
    const unfoundWords = this.targetWords.filter(w => !this.foundWords.includes(w));
    if (unfoundWords.length === 0) return;
    
    // Use current hint word if valid and still unfound, else pick first unfound
    if (!this.currentHint || !unfoundWords.includes(this.currentHint.word)) {
      this.currentHint = { word: unfoundWords[0], length: 0 };
    }
    
    // Find solution for this word
    const sol = this.levelData.solution.find(s => s.word === this.currentHint!.word);
    if (!sol) return;
    
    const wordLen = this.currentHint!.word.length;
    if (this.currentHint!.length >= wordLen) return; // Full word already hinted
    
    // Calculate position for the next letter
    const dx = Math.sign(sol.end[0] - sol.start[0]);
    const dy = Math.sign(sol.end[1] - sol.start[1]);
    
    const hx = sol.start[0] + dx * this.currentHint!.length;
    const hy = sol.start[1] + dy * this.currentHint!.length;
    
    // Highlight it
    this.grid[hy][hx].isHinted = true;
    
    // Increment hint length
    this.currentHint!.length++;
  }

  ngOnDestroy() {
    this.stopTimer();
  }

  // --- Interaction Logic ---
  
  onTouchStart(event: TouchEvent | MouseEvent, cell: GridCell) {
    if (this.isCompleted) return;
    event.preventDefault(); // Prevent scrolling
    this.isSelecting = true;
    this.startCell = cell;
    this.updateSelection(cell);
  }

  @HostListener('window:touchmove', ['$event'])
  @HostListener('window:mousemove', ['$event'])
  onMove(event: TouchEvent | MouseEvent) {
    if (!this.isSelecting || !this.startCell || this.isCompleted) return;
    event.preventDefault();
    
    let clientX, clientY;
    if (event instanceof TouchEvent) {
      clientX = event.touches[0].clientX;
      clientY = event.touches[0].clientY;
    } else {
      clientX = event.clientX;
      clientY = event.clientY;
    }
    
    const element = document.elementFromPoint(clientX, clientY);
    if (element && element.classList.contains('letter-cell')) {
      const x = parseInt(element.getAttribute('data-x') || '-1', 10);
      const y = parseInt(element.getAttribute('data-y') || '-1', 10);
      
      if (x >= 0 && y >= 0) {
        this.updateSelection(this.grid[y][x]);
      }
    }
  }

  @HostListener('window:touchend', ['$event'])
  @HostListener('window:mouseup', ['$event'])
  onEnd(event: TouchEvent | MouseEvent) {
    if (!this.isSelecting) return;
    this.isSelecting = false;
    
    this.checkSelectedWord();
    
    // Clear selection UI
    this.grid.forEach(row => row.forEach(c => c.isSelected = false));
    this.currentSelection = [];
  }

  updateSelection(endCell: GridCell) {
    // Clear old selection
    this.grid.forEach(row => row.forEach(c => c.isSelected = false));
    this.currentSelection = [];
    
    // Must be in a straight line (horizontal, vertical, diagonal)
    const dx = endCell.x - this.startCell!.x;
    const dy = endCell.y - this.startCell!.y;
    
    // Check if straight line
    if (dx === 0 || dy === 0 || Math.abs(dx) === Math.abs(dy)) {
      const steps = Math.max(Math.abs(dx), Math.abs(dy));
      const stepX = dx === 0 ? 0 : Math.sign(dx);
      const stepY = dy === 0 ? 0 : Math.sign(dy);
      
      for (let i = 0; i <= steps; i++) {
        const cx = this.startCell!.x + stepX * i;
        const cy = this.startCell!.y + stepY * i;
        const cell = this.grid[cy][cx];
        cell.isSelected = true;
        this.currentSelection.push(cell);
      }
    } else {
      // Just select start cell if dragging wildly
      this.startCell!.isSelected = true;
      this.currentSelection.push(this.startCell!);
    }
  }

  checkSelectedWord() {
    if (this.currentSelection.length < 2) return;
    
    const wordStr = this.currentSelection.map(c => c.letter).join('');
    const wordStrRev = this.currentSelection.slice().reverse().map(c => c.letter).join('');
    
    let matchedWord = null;
    if (this.targetWords.includes(wordStr) && !this.foundWords.includes(wordStr)) {
      matchedWord = wordStr;
    } else if (this.targetWords.includes(wordStrRev) && !this.foundWords.includes(wordStrRev)) {
      matchedWord = wordStrRev;
    }
    
    if (matchedWord) {
      this.foundWords.push(matchedWord);
      const colorIndex = (this.foundWords.length - 1) % this.colors.length;
      
      this.currentSelection.forEach(c => {
        c.isFound = true;
        c.color = this.colors[colorIndex];
      });
      
      this.checkCompletion();
    }
  }

  checkCompletion() {
    if (this.foundWords.length === this.targetWords.length) {
      this.isCompleted = true;
      this.stopTimer();
      this.submitCompletion();
    }
  }

  private submitCompletion() {
    this.gamesService.completeWordSearch(this.timer, this.foundWords).subscribe({
      next: async (res) => {
        this.alreadyCompletedToday = true;
        
        if (res.points_awarded > 0 && this.authService) {
          const profile = this.authService.currentUserValue;
          if (profile) {
            const updatedProfile = { 
              ...profile, 
              xp: res.new_xp, 
              streak: res.current_streak 
            };
            this.authService.updateLocalProfile(updatedProfile);
          }
          
          const toast = await this.toastCtrl.create({
            message: `${res.message} +${res.points_awarded} XP! Streak: ${res.current_streak}`,
            duration: 3000,
            color: 'success',
            position: 'top'
          });
          toast.present();
        } else {
          const toast = await this.toastCtrl.create({
            message: res.message,
            duration: 2000,
            color: 'success',
            position: 'top'
          });
          toast.present();
        }
      }
    });
  }
}
