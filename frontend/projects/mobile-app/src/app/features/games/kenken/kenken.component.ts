import { Component, OnInit, OnDestroy, inject, HostListener, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { IonicModule, ToastController } from '@ionic/angular';
import { GamesService } from '../../../services/games.service';
import { addIcons } from 'ionicons';
import { arrowBackOutline, refreshOutline, trophyOutline, backspaceOutline, bulbOutline } from 'ionicons/icons';

interface Cage {
  id: number;
  cells: [number, number][];
  op: string;
  target: number;
  isValid?: boolean; // green highlight
  isInvalid?: boolean; // red highlight
}

import { LoaderComponent } from '../../../shared/components/loader/loader.component';

@Component({
  selector: 'app-kenken',
  standalone: true,
  imports: [CommonModule, IonicModule, FormsModule, LoaderComponent],
  templateUrl: './kenken.component.html',
  styleUrls: ['./kenken.component.scss']
})
export class KenKenComponent implements OnInit, OnDestroy {
  private gamesService = inject(GamesService);
  private router = inject(Router);
  private toastCtrl = inject(ToastController);
  
  Math = Math;

  size: number = 4;
  grid: number[][] = [];
  solution: number[][] = [];
  cages: Cage[] = [];
  cellToCage: { [key: string]: Cage } = {};
  
  selectedCell: [number, number] | null = null;
  conflicts: boolean[][] = [];

  elapsedSeconds: number = 0;
  won: boolean = false;
  hasStarted: boolean = false;
  isLoading: boolean = true;
  
  private timerInterval: any;
  private firstGameCompletedToday: boolean = false;

  constructor() {
    addIcons({ arrowBackOutline, refreshOutline, trophyOutline, backspaceOutline, bulbOutline });
  }

  ngOnInit() {
    this.loadPuzzle();
  }

  ngOnDestroy() {
    this.stopTimer();
  }

  goBack() {
    this.router.navigateByUrl('/games');
  }
  
  loadPuzzle() {
    this.isLoading = true;
    this.gamesService.getTodayKenKen(this.size).subscribe({
      next: (res: any) => {
        if (res.completed) {
          this.firstGameCompletedToday = true;
        }
        if (res.level) {
          this.setupBoard(res.level);
          
          if (res.completed && res.saved_state && res.saved_state.grid) {
            this.grid = res.saved_state.grid;
          } else if (res.completed) {
            this.grid = res.level.solution;
          }
        }
        
        if (res.completed) {
          this.won = true;
          if (res.saved_state && res.saved_state.time_taken !== undefined) {
            this.elapsedSeconds = res.saved_state.time_taken;
          }
        }
        this.isLoading = false;
      },
      error: () => {
        // Fallback or retry
        this.isLoading = false;
      }
    });
  }

  setupBoard(level: any) {
    this.stopTimer();
    this.elapsedSeconds = 0;
    this.won = false;
    this.hasStarted = false;
    this.selectedCell = null;
    
    this.size = level.size;
    this.solution = level.solution;
    this.cages = level.cages;
    
    this.grid = Array.from({ length: this.size }, () => Array(this.size).fill(0));
    this.conflicts = Array.from({ length: this.size }, () => Array(this.size).fill(false));
    
    this.cellToCage = {};
    for (const cage of this.cages) {
      cage.isValid = false;
      cage.isInvalid = false;
      for (const [r, c] of cage.cells) {
        this.cellToCage[`${r},${c}`] = cage;
      }
    }
  }

  selectCell(r: number, c: number) {
    if (this.won) return;
    this.selectedCell = [r, c];
  }

  @HostListener('window:keydown', ['$event'])
  handleKeyboardEvent(event: KeyboardEvent) {
    if (this.won || !this.selectedCell) return;
    
    const key = event.key;
    if (key >= '1' && key <= this.size.toString()) {
      this.inputNumber(parseInt(key, 10));
    } else if (key === 'Backspace' || key === 'Delete') {
      this.clearCell();
    } else if (key === 'ArrowUp' && this.selectedCell[0] > 0) {
      this.selectedCell = [this.selectedCell[0] - 1, this.selectedCell[1]];
    } else if (key === 'ArrowDown' && this.selectedCell[0] < this.size - 1) {
      this.selectedCell = [this.selectedCell[0] + 1, this.selectedCell[1]];
    } else if (key === 'ArrowLeft' && this.selectedCell[1] > 0) {
      this.selectedCell = [this.selectedCell[0], this.selectedCell[1] - 1];
    } else if (key === 'ArrowRight' && this.selectedCell[1] < this.size - 1) {
      this.selectedCell = [this.selectedCell[0], this.selectedCell[1] + 1];
    }
  }

  inputNumber(num: number) {
    if (this.won || !this.selectedCell) return;
    if (!this.hasStarted) {
      this.startTimer();
      this.hasStarted = true;
    }
    
    const [r, c] = this.selectedCell;
    this.grid[r][c] = num;
    this.validateBoard();
  }
  
  clearCell() {
    if (this.won || !this.selectedCell) return;
    const [r, c] = this.selectedCell;
    this.grid[r][c] = 0;
    this.validateBoard();
  }

  validateBoard() {
    let hasEmpty = false;
    let hasConflict = false;
    
    // Reset conflicts
    for (let r = 0; r < this.size; r++) {
      for (let c = 0; c < this.size; c++) {
        this.conflicts[r][c] = false;
        if (this.grid[r][c] === 0) hasEmpty = true;
      }
    }
    
    // Check row/col duplicates
    for (let r = 0; r < this.size; r++) {
      for (let c = 0; c < this.size; c++) {
        const val = this.grid[r][c];
        if (val === 0) continue;
        
        for (let i = 0; i < this.size; i++) {
          if (i !== c && this.grid[r][i] === val) {
            this.conflicts[r][c] = true;
            this.conflicts[r][i] = true;
            hasConflict = true;
          }
          if (i !== r && this.grid[i][c] === val) {
            this.conflicts[r][c] = true;
            this.conflicts[i][c] = true;
            hasConflict = true;
          }
        }
      }
    }
    
    // Check cages
    let allCagesValid = true;
    for (const cage of this.cages) {
      let isFull = true;
      const vals: number[] = [];
      for (const [r, c] of cage.cells) {
        if (this.grid[r][c] === 0) {
          isFull = false;
          break;
        }
        vals.push(this.grid[r][c]);
      }
      
      if (!isFull) {
        cage.isValid = false;
        cage.isInvalid = false;
        allCagesValid = false;
        continue;
      }
      
      // Evaluate cage
      const target = cage.target;
      const op = cage.op;
      let valid = false;
      
      if (op === '') {
        valid = vals[0] === target;
      } else if (op === '+') {
        valid = vals.reduce((a, b) => a + b, 0) === target;
      } else if (op === '*') {
        valid = vals.reduce((a, b) => a * b, 1) === target;
      } else if (op === '-') {
        valid = Math.abs(vals[0] - vals[1]) === target;
      } else if (op === '/') {
        valid = (vals[0] === vals[1] * target) || (vals[1] === vals[0] * target);
      }
      
      cage.isValid = valid;
      cage.isInvalid = !valid;
      if (!valid) allCagesValid = false;
    }
    
    if (!hasEmpty && !hasConflict && allCagesValid) {
      this.handleWin();
    }
  }

  showHint() {
    if (this.won) return;
    
    // Find first incorrect or empty cell
    for (let r = 0; r < this.size; r++) {
      for (let c = 0; c < this.size; c++) {
        if (this.grid[r][c] !== this.solution[r][c]) {
          this.grid[r][c] = this.solution[r][c];
          
          // Flash the cell briefly to show it was hinted
          this.selectedCell = [r, c];
          setTimeout(() => {
            if (this.selectedCell && this.selectedCell[0] === r && this.selectedCell[1] === c) {
              this.selectedCell = null;
            }
          }, 1000);
          
          this.validateBoard();
          return;
        }
      }
    }
  }

  startTimer() {
    this.timerInterval = setInterval(() => {
      this.elapsedSeconds++;
    }, 1000);
  }

  stopTimer() {
    if (this.timerInterval) {
      clearInterval(this.timerInterval);
      this.timerInterval = null;
    }
  }

  get formattedTime(): string {
    const m = Math.floor(this.elapsedSeconds / 60);
    const s = this.elapsedSeconds % 60;
    return `${m}:${s.toString().padStart(2, '0')}`;
  }

  private cdr = inject(ChangeDetectorRef);

  handleWin() {
    this.won = true;
    this.stopTimer();
    this.selectedCell = null;
    this.cdr.detectChanges(); // Force immediate view update
    
    this.gamesService.completeKenKen(this.elapsedSeconds, this.size).subscribe(async (res: any) => {
      if (!this.firstGameCompletedToday && res.points_awarded > 0) {
        this.firstGameCompletedToday = true;
        const toast = await this.toastCtrl.create({
          message: `Awesome! You earned ${res.points_awarded} XP!`,
          duration: 3000,
          position: 'top',
          color: 'success',
          icon: 'trophy-outline'
        });
        toast.present();
      }
    });
  }

  getCageLabel(r: number, c: number): string | null {
    const cage = this.cellToCage[`${r},${c}`];
    if (!cage) return null;
    // Only display label in the top-left-most cell of the cage
    let minR = this.size;
    let minC = this.size;
    for (const [cr, cc] of cage.cells) {
      if (cr < minR || (cr === minR && cc < minC)) {
        minR = cr;
        minC = cc;
      }
    }
    if (r === minR && c === minC) {
      return `${cage.target}${cage.op}`;
    }
    return null;
  }

  getBorders(r: number, c: number): any {
    const cage = this.cellToCage[`${r},${c}`];
    if (!cage) return {};
    
    const borders: any = {};
    const cellsStr = cage.cells.map(([cr, cc]) => `${cr},${cc}`);
    
    // Default thin borders
    borders.borderRight = '1px solid var(--grid-line, var(--ion-color-light-shade))';
    borders.borderBottom = '1px solid var(--grid-line, var(--ion-color-light-shade))';
    
    // Thick borders for cage boundaries
    if (!cellsStr.includes(`${r},${c + 1}`)) borders.borderRight = '2px solid var(--cage-border, var(--ion-color-medium))';
    if (!cellsStr.includes(`${r + 1},${c}`)) borders.borderBottom = '2px solid var(--cage-border, var(--ion-color-medium))';
    
    // Remove outer edge borders to let the board container handle it
    if (c === this.size - 1) borders.borderRight = 'none';
    if (r === this.size - 1) borders.borderBottom = 'none';
    
    return borders;
  }
}
