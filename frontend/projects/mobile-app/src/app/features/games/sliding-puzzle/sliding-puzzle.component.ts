import { Component, OnInit, OnDestroy, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { IonicModule, ToastController } from '@ionic/angular';
import { GamesService } from '../../../services/games.service';
import { addIcons } from 'ionicons';
import { arrowBackOutline, refreshOutline, trophyOutline, bulbOutline, refresh, bulb, arrowUpOutline, arrowDownOutline, arrowForwardOutline } from 'ionicons/icons';

@Component({
  selector: 'app-sliding-puzzle',
  standalone: true,
  imports: [CommonModule, IonicModule],
  templateUrl: './sliding-puzzle.component.html',
  styleUrls: ['./sliding-puzzle.component.scss']
})
export class SlidingPuzzleComponent implements OnInit, OnDestroy {
  private gamesService = inject(GamesService);
  private router = inject(Router);
  private toastCtrl = inject(ToastController);

  boardSize: number = 4;
  tiles: number[] = [];
  initialTiles: number[] = [];
  initialSolutionPath: number[] = [];
  currentSolutionPath: number[] = [];
  moveCount: number = 0;
  elapsedSeconds: number = 0;
  won: boolean = false;
  hasStarted: boolean = false;
  hintTile: number | null = null;
  hintDirection: string | null = null;
  
  private timerInterval: any;
  private firstGameCompletedToday: boolean = false;

  constructor() {
    addIcons({ arrowBackOutline, refreshOutline, trophyOutline, bulbOutline, refresh, bulb, arrowUpOutline, arrowDownOutline, arrowForwardOutline });
  }

  ngOnInit() {
    this.gamesService.getTodaySlidingPuzzle().subscribe({
      next: (res: any) => {
        if (res.completed) {
          this.firstGameCompletedToday = true;
        }
        if (res.level) {
          this.boardSize = res.level.board_size;
          this.initialTiles = res.level.tiles;
          this.initialSolutionPath = res.level.solution_path || [];
        }
        this.initGame();
        
        if (res.completed) {
          this.won = true;
          this.tiles = Array.from({ length: this.boardSize * this.boardSize - 1 }, (_, i) => i + 1).concat([0]);
          if (res.saved_state) {
            this.elapsedSeconds = res.saved_state.time_taken || 0;
            this.moveCount = res.saved_state.move_count || 0;
          }
        }
      },
      error: () => {
        // Fallback for testing if backend fails
        this.boardSize = 3;
        this.initialTiles = [1, 2, 3, 4, 5, 6, 7, 0, 8]; // sample shuffled
        this.initialSolutionPath = [8];
        this.initGame();
      }
    });
  }

  ngOnDestroy() {
    this.stopTimer();
  }

  goBack() {
    this.router.navigateByUrl('/games');
  }

  initGame() {
    this.stopTimer();
    this.moveCount = 0;
    this.elapsedSeconds = 0;
    this.won = false;
    this.hasStarted = false;
    this.hintTile = null;
    
    if (this.initialTiles && this.initialTiles.length > 0) {
      this.tiles = [...this.initialTiles];
      this.currentSolutionPath = [...this.initialSolutionPath];
    } else {
      // Fallback
      const totalTiles = this.boardSize * this.boardSize;
      this.tiles = Array.from({ length: totalTiles - 1 }, (_, i) => i + 1);
      this.tiles.push(0);
      this.tiles[totalTiles - 1] = this.tiles[totalTiles - 2];
      this.tiles[totalTiles - 2] = 0; // Just one move away for fallback
      this.currentSolutionPath = [this.tiles[totalTiles - 1]];
    }
  }

  getValidNeighbors(index: number): number[] {
    const neighbors: number[] = [];
    const size = this.boardSize;
    const row = Math.floor(index / size);
    const col = index % size;

    if (row > 0) neighbors.push(index - size); // Up
    if (row < size - 1) neighbors.push(index + size); // Down
    if (col > 0) neighbors.push(index - 1); // Left
    if (col < size - 1) neighbors.push(index + 1); // Right

    return neighbors;
  }

  onTileClick(index: number) {
    if (this.won) return;

    const blankIdx = this.tiles.indexOf(0);
    const neighbors = this.getValidNeighbors(blankIdx);

    if (neighbors.includes(index)) {
      if (!this.hasStarted) {
        this.startTimer();
        this.hasStarted = true;
      }
      
      const movedTile = this.tiles[index];

      // Swap tiles
      this.tiles[blankIdx] = movedTile;
      this.tiles[index] = 0;
      this.moveCount++;
      this.hintTile = null;
      this.hintDirection = null;
      
      // Rubber-band solution path logic
      if (this.currentSolutionPath.length > 0 && this.currentSolutionPath[0] === movedTile) {
        // The user made the correct next move in the path
        this.currentSolutionPath.shift();
      } else {
        // The user made a move that deviates from the path.
        // The optimal way to get back onto the solution path is to immediately undo this move.
        this.currentSolutionPath.unshift(movedTile);
      }

      // Check win
      if (this.checkWin(this.tiles)) {
        this.handleWin();
      }
    }
  }

  showHint() {
    if (this.won || this.currentSolutionPath.length === 0) return;
    
    // The next required tile to move is always at the head of the path
    const targetTile = this.currentSolutionPath[0];
    const currentIndex = this.tiles.indexOf(targetTile);
    const blankIdx = this.tiles.indexOf(0);
    
    this.hintTile = targetTile;
    
    // Direction points from the target tile towards the blank space (since it MUST slide into the blank space)
    const currentRow = Math.floor(currentIndex / this.boardSize);
    const currentCol = currentIndex % this.boardSize;
    const blankRow = Math.floor(blankIdx / this.boardSize);
    const blankCol = blankIdx % this.boardSize;
    
    const rowDiff = blankRow - currentRow;
    const colDiff = blankCol - currentCol;
    
    if (Math.abs(rowDiff) > Math.abs(colDiff)) {
      this.hintDirection = rowDiff < 0 ? 'up' : 'down';
    } else {
      this.hintDirection = colDiff < 0 ? 'back' : 'forward';
    }
    
    // Auto-hide hint after 3 seconds
    setTimeout(() => {
      if (this.hintTile === targetTile) {
        this.hintTile = null;
        this.hintDirection = null;
      }
    }, 3000);
  }

  // Keyboard accessibility
  onTileKeyDown(event: KeyboardEvent, index: number) {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      this.onTileClick(index);
    }
  }

  checkWin(currentTiles: number[]): boolean {
    const totalTiles = this.boardSize * this.boardSize;
    for (let i = 0; i < totalTiles - 1; i++) {
      if (currentTiles[i] !== i + 1) return false;
    }
    return currentTiles[totalTiles - 1] === 0;
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

  handleWin() {
    this.won = true;
    this.stopTimer();
    
    this.gamesService.completeSlidingPuzzle(this.elapsedSeconds, this.moveCount, this.boardSize).subscribe(async (res: any) => {
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
}
