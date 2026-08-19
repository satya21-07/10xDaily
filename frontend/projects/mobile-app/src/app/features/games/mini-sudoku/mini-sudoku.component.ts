import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { IonicModule, ToastController } from '@ionic/angular';
import { GamesService, MiniSudokuLevel } from '../../../services/games.service';
import { AuthService } from '../../../services/auth.service';
import { addIcons } from 'ionicons';
import { refresh, backspace, bulb, arrowBackOutline } from 'ionicons/icons';

interface SudokuCell {
  row: number;
  col: number;
  val: number;
  isFixed: boolean;
  hasError: boolean;
  isSelected: boolean;
  isHinted?: boolean;
  animateComplete?: boolean;
}

import { LoaderComponent } from '../../../shared/components/loader/loader.component';

@Component({
  selector: 'app-mini-sudoku',
  standalone: true,
  imports: [CommonModule, IonicModule, LoaderComponent],
  templateUrl: './mini-sudoku.component.html',
  styleUrls: ['./mini-sudoku.component.scss']
})
export class MiniSudokuComponent implements OnInit {
  private gamesService = inject(GamesService);
  private authService = inject(AuthService);
  private router = inject(Router);
  private toastCtrl = inject(ToastController);

  levelData: MiniSudokuLevel | null = null;
  grid: SudokuCell[][] = [];
  
  // Timer state
  timer: number = 0;
  timerInterval: any;
  timerFormatted: string = '00:00';
  
  isCompleted = false;
  alreadyCompletedToday = false;
  savedState: any = null;
  isLoading = true;

  selectedCell: SudokuCell | null = null;
  numpad = [1, 2, 3, 4, 5, 6];

  constructor() {
    addIcons({ refresh, backspace, bulb, arrowBackOutline });
  }

  ngOnInit() {
    this.isLoading = true;
    this.gamesService.getTodayMiniSudoku().subscribe({
      next: (res) => {
        this.alreadyCompletedToday = res.completed;
        this.levelData = res.level;
        this.savedState = res.saved_state;
        this.initGame();
        this.isLoading = false;
      },
      error: () => {
        this.isLoading = false;
      }
    });
  }

  initGame() {
    if (!this.levelData) return;
    
    this.timer = 0;
    this.updateTimerDisplay();
    this.isCompleted = false;
    this.selectedCell = null;
    
    // Initialize Grid
    this.grid = [];
    for (let r = 0; r < 6; r++) {
      const row: SudokuCell[] = [];
      for (let c = 0; c < 6; c++) {
        const val = this.levelData.grid[r][c];
        row.push({
          row: r,
          col: c,
          val: val,
          isFixed: val !== 0,
          hasError: false,
          isSelected: false
        });
      }
      this.grid.push(row);
    }
    
    // Load saved state
    if (this.savedState) {
      this.timer = this.savedState.time_taken || 0;
      this.updateTimerDisplay();
      
      const savedGrid = this.savedState.grid;
      if (savedGrid) {
        for (let r = 0; r < 6; r++) {
          for (let c = 0; c < 6; c++) {
            if (!this.grid[r][c].isFixed) {
              this.grid[r][c].val = savedGrid[r][c];
            }
          }
        }
      }
      
      this.validateGrid();
      
      if (this.alreadyCompletedToday || this.checkWinCondition()) {
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

  selectCell(cell: SudokuCell) {
    if (this.isCompleted || cell.isFixed) return;
    
    if (this.selectedCell) {
      this.selectedCell.isSelected = false;
    }
    this.selectedCell = cell;
    cell.isSelected = true;
  }

  inputNumber(num: number) {
    if (!this.selectedCell || this.isCompleted) return;
    this.selectedCell.val = num;
    this.selectedCell.isHinted = false;
    this.validateGrid();
    this.checkCompletedZones();
    
    if (this.checkWinCondition()) {
      this.isCompleted = true;
      this.stopTimer();
      this.selectedCell.isSelected = false;
      this.selectedCell = null;
      this.submitCompletion();
    }
  }

  eraseNumber() {
    if (!this.selectedCell || this.isCompleted) return;
    this.selectedCell.val = 0;
    this.selectedCell.isHinted = false;
    this.validateGrid();
  }

  showHint() {
    if (this.isCompleted || !this.levelData) return;
    
    let targetCell = this.selectedCell;
    
    if (!targetCell || targetCell.isFixed || targetCell.val === this.levelData.solution[targetCell.row][targetCell.col]) {
      // Find the first empty or wrong cell
      let found = false;
      for (let r = 0; r < 6 && !found; r++) {
        for (let c = 0; c < 6 && !found; c++) {
          const cell = this.grid[r][c];
          if (!cell.isFixed && cell.val !== this.levelData.solution[r][c]) {
            targetCell = cell;
            found = true;
          }
        }
      }
    }
    
    if (targetCell) {
      if (this.selectedCell) this.selectedCell.isSelected = false;
      this.selectedCell = targetCell;
      targetCell.isSelected = true;
      targetCell.val = this.levelData.solution[targetCell.row][targetCell.col];
      targetCell.isHinted = true;
      this.validateGrid();
      this.checkCompletedZones();
      
      if (this.checkWinCondition()) {
        this.isCompleted = true;
        this.stopTimer();
        this.selectedCell.isSelected = false;
        this.selectedCell = null;
        this.submitCompletion();
      }
    }
  }

  validateGrid() {
    // Reset all errors
    for (let r = 0; r < 6; r++) {
      for (let c = 0; c < 6; c++) {
        this.grid[r][c].hasError = false;
      }
    }
    
    // Check for duplicates
    for (let r = 0; r < 6; r++) {
      for (let c = 0; c < 6; c++) {
        const val = this.grid[r][c].val;
        if (val === 0) continue;
        
        let hasDuplicate = false;
        
        // Check row
        for (let i = 0; i < 6; i++) {
          if (i !== c && this.grid[r][i].val === val) hasDuplicate = true;
        }
        
        // Check col
        for (let i = 0; i < 6; i++) {
          if (i !== r && this.grid[i][c].val === val) hasDuplicate = true;
        }
        
        // Check 2x3 block
        const startRow = r - (r % 2);
        const startCol = c - (c % 3);
        for (let i = 0; i < 2; i++) {
          for (let j = 0; j < 3; j++) {
            const currR = startRow + i;
            const currC = startCol + j;
            if ((currR !== r || currC !== c) && this.grid[currR][currC].val === val) {
              hasDuplicate = true;
            }
          }
        }
        
        if (hasDuplicate) {
          this.grid[r][c].hasError = true;
        }
      }
    }
  }
  
  completedZones = new Set<string>();

  checkCompletedZones() {
    const checkSet = (cells: SudokuCell[], zoneId: string) => {
      const vals = cells.map(c => c.val);
      const isCompleteAndValid = vals.every(v => v !== 0) && new Set(vals).size === 6 && !cells.some(c => c.hasError);
      
      if (isCompleteAndValid && !this.completedZones.has(zoneId)) {
        this.completedZones.add(zoneId);
        cells.forEach(c => {
          c.animateComplete = true;
          setTimeout(() => c.animateComplete = false, 1000); // Remove animation after 1s
        });
      }
    };

    // Check rows
    for (let r = 0; r < 6; r++) {
      checkSet(this.grid[r], `row-${r}`);
    }
    
    // Check cols
    for (let c = 0; c < 6; c++) {
      const colCells = [];
      for (let r = 0; r < 6; r++) colCells.push(this.grid[r][c]);
      checkSet(colCells, `col-${c}`);
    }
    
    // Check blocks
    for (let br = 0; br < 3; br++) {
      for (let bc = 0; bc < 2; bc++) {
        const blockCells = [];
        const startRow = br * 2;
        const startCol = bc * 3;
        for (let i = 0; i < 2; i++) {
          for (let j = 0; j < 3; j++) {
            blockCells.push(this.grid[startRow + i][startCol + j]);
          }
        }
        checkSet(blockCells, `block-${br}-${bc}`);
      }
    }
  }

  checkWinCondition(): boolean {
    let allFilledAndValid = true;
    for (let r = 0; r < 6; r++) {
      for (let c = 0; c < 6; c++) {
        if (this.grid[r][c].val === 0 || this.grid[r][c].hasError) {
          allFilledAndValid = false;
        }
      }
    }
    return allFilledAndValid;
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
    this.router.navigateByUrl('/games');
  }

  reset() {
    this.stopTimer();
    this.savedState = null;
    this.initGame();
  }

  ngOnDestroy() {
    this.stopTimer();
  }

  private submitCompletion() {
    const simpleGrid = this.grid.map(row => row.map(cell => cell.val));
    this.gamesService.completeMiniSudoku(this.timer, simpleGrid).subscribe({
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
