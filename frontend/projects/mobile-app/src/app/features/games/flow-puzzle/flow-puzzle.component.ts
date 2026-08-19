import { Component, ElementRef, HostListener, OnInit, OnDestroy, ViewChild, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { IonicModule, ToastController } from '@ionic/angular';
import { GamesService, FlowLevel, TodayFlowResponse } from '../../../services/games.service';
import { AuthService } from '../../../services/auth.service';
import { addIcons } from 'ionicons';
import { refresh, arrowUndo, bulb, arrowBackOutline } from 'ionicons/icons';

interface Cell {
  x: number;
  y: number;
  color: string | null;
  isEndpoint: boolean;
  endpointId?: string;
  pathId?: string;
  connections: {
    top: boolean;
    right: boolean;
    bottom: boolean;
    left: boolean;
  };
}

import { LoaderComponent } from '../../../shared/components/loader/loader.component';

@Component({
  selector: 'app-flow-puzzle',
  standalone: true,
  imports: [CommonModule, IonicModule, LoaderComponent],
  templateUrl: './flow-puzzle.component.html',
  styleUrls: ['./flow-puzzle.component.scss']
})
export class FlowPuzzleComponent implements OnInit, OnDestroy {
  private gamesService = inject(GamesService);
  private authService = inject(AuthService);
  private router = inject(Router);
  private toastCtrl = inject(ToastController);

  constructor() {
    addIcons({ refresh, arrowUndo, bulb, arrowBackOutline });
  }

  levelData: FlowLevel | null = null;
  grid: Cell[][] = [];
  gridSize = 0;
  
  moves = 0;
  completedLines = 0;
  totalLines = 0;
  fillPercentage = 0;
  isCompleted = false;
  alreadyCompletedToday = false;
  isLoading = true;

  paths: Map<string, {x: number, y: number}[]> = new Map();
  currentDragPath: string | null = null;

  savedPaths: any = null;

  timeElapsed = 0;
  timerInterval: any;

  ngOnInit() {
    this.isLoading = true;
    this.gamesService.getTodayFlowPuzzle().subscribe({
      next: (res) => {
        this.alreadyCompletedToday = res.completed;
        this.levelData = res.level;
        this.savedPaths = res.saved_paths;
        this.initGame();
        this.isLoading = false;
      },
      error: () => {
        this.isLoading = false;
      }
    });
  }

  ngOnDestroy() {
    if (this.timerInterval) {
      clearInterval(this.timerInterval);
    }
  }

  get formattedTime(): string {
    const minutes = Math.floor(this.timeElapsed / 60);
    const seconds = this.timeElapsed % 60;
    return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
  }

  initGame() {
    if (!this.levelData) return;
    this.gridSize = this.levelData.grid_size;
    this.totalLines = this.levelData.colors.length;
    this.moves = 0;
    this.paths.clear();
    this.currentDragPath = null;
    this.isCompleted = false;
    this.timeElapsed = 0;
    if (this.timerInterval) clearInterval(this.timerInterval);

    // Initialize empty grid
    this.grid = Array(this.gridSize).fill(null).map((_, y) => 
      Array(this.gridSize).fill(null).map((_, x) => ({
        x, y,
        color: null,
        isEndpoint: false,
        connections: { top: false, right: false, bottom: false, left: false }
      }))
    );

    // Place endpoints
    this.levelData.colors.forEach(c => {
      const startCell = this.grid[c.start[1]][c.start[0]];
      const endCell = this.grid[c.end[1]][c.end[0]];
      
      startCell.color = c.color;
      startCell.isEndpoint = true;
      startCell.endpointId = c.id;
      
      endCell.color = c.color;
      endCell.isEndpoint = true;
      endCell.endpointId = c.id;
      
      this.paths.set(c.id, []);
    });
    
    // Load saved paths if any
    if (this.savedPaths) {
      Object.keys(this.savedPaths).forEach(key => {
        const path = this.savedPaths[key];
        const colorDef = this.levelData?.colors.find(c => c.id === key);
        if (path && path.length > 0 && colorDef) {
          const newPath: {x: number, y: number}[] = [];
          path.forEach((p: any) => {
            newPath.push({x: p.x, y: p.y});
            const c = this.grid[p.y][p.x];
            c.color = colorDef.color;
            if (!c.isEndpoint) {
              c.pathId = key;
            }
          });
          this.paths.set(key, newPath);
          this.updateConnections(key);
        }
      });
    }

    if (this.alreadyCompletedToday) {
      this.isCompleted = true;
    }
    
    this.updateStats();
    
    if (!this.isCompleted) {
      this.timerInterval = setInterval(() => {
        this.timeElapsed++;
      }, 1000);
    }
  }

  goBack() {
    this.router.navigateByUrl('/games');
  }

  reset() {
    this.savedPaths = null;
    this.initGame();
  }

  undo() {
    // Simple undo: remove the last drawn path, or just reset for now if too complex
    // For a real implementation, we could keep a history of path additions
    // Let's implement a quick clear of the last moved path
    this.reset();
  }

  hint() {
    if (this.isCompleted) return;
    
    // Find a color that is not connected yet
    for (const color of this.levelData?.colors || []) {
      const isConnected = this.isPathConnected(color.id);
      
      if (!isConnected) {
        if (color.solution_path) {
          const currentPath = this.paths.get(color.id) || [];
          
          // Check if current path starts from the end endpoint
          let isReversed = false;
          if (currentPath.length > 0) {
            const firstCell = currentPath[0];
            const endSol = color.solution_path[color.solution_path.length - 1];
            if (firstCell.x === endSol[0] && firstCell.y === endSol[1]) {
              isReversed = true;
            }
          }
          
          const targetPath = isReversed ? [...color.solution_path].reverse() : color.solution_path;
          
          // Determine how much of the current path is correct
          let correctLength = 0;
          for (let i = 0; i < currentPath.length; i++) {
            if (i < targetPath.length) {
              const solPos = targetPath[i];
              const curPos = currentPath[i];
              if (solPos[0] === curPos.x && solPos[1] === curPos.y) {
                correctLength++;
              } else {
                break;
              }
            } else {
              break;
            }
          }
          
          // If the user's path diverges, truncate the incorrect part
          if (correctLength < currentPath.length) {
            if (correctLength === 0) {
              this.clearPath(color.id);
            } else {
              const lastCorrectCell = this.grid[currentPath[correctLength - 1].y][currentPath[correctLength - 1].x];
              this.truncatePathTo(color.id, lastCorrectCell);
            }
          }
          
          // If correctLength is 0, we need to add the start cell first
          if (correctLength === 0) {
             const startSol = targetPath[0];
             const startCell = this.grid[startSol[1]][startSol[0]];
             this.addToPath(color.id, startCell);
             correctLength = 1;
          }
          
          // Now add the next cell from the solution path
          if (correctLength < targetPath.length) {
            const nextSol = targetPath[correctLength];
            const nextCell = this.grid[nextSol[1]][nextSol[0]];
            
            // If the next cell is occupied by a DIFFERENT path, truncate that path!
            if (nextCell.color && nextCell.color !== color.color && !nextCell.isEndpoint) {
              const otherPathId = nextCell.pathId;
              if (otherPathId) {
                this.truncatePathBefore(otherPathId, nextCell);
              }
            }
            
            this.addToPath(color.id, nextCell);
            this.moves++;
            this.checkCompletion();
            return;
          }
        }
      }
    }
    
    // If no hint available
    this.toastCtrl.create({
      message: 'No hints available right now.',
      duration: 2000,
      position: 'top',
      color: 'warning'
    }).then(toast => toast.present());
  }

  private isPathConnected(pathId: string): boolean {
    const path = this.paths.get(pathId) || [];
    if (path.length < 2) return false;
    const first = path[0];
    const last = path[path.length - 1];
    const firstCell = this.grid[first.y][first.x];
    const lastCell = this.grid[last.y][last.x];
    return firstCell.isEndpoint && firstCell.endpointId === pathId &&
           lastCell.isEndpoint && lastCell.endpointId === pathId;
  }

  onTouchStart(event: TouchEvent, cell: Cell) {
    if (this.isCompleted) return;
    event.preventDefault(); // prevent scrolling
    
    // If starting on an endpoint or an existing path
    if (cell.color) {
      // Find which path this is
      const colorDef = this.levelData?.colors.find(c => c.color === cell.color);
      if (colorDef) {
        this.currentDragPath = colorDef.id;
        
        // If it's an endpoint, clear the existing path for this color to start fresh from here
        if (cell.isEndpoint) {
           this.clearPath(colorDef.id);
           this.addToPath(colorDef.id, cell);
        } else {
           // If it's middle of path, truncate path to this point
           this.truncatePathTo(colorDef.id, cell);
        }
      }
    }
  }

  @HostListener('window:touchmove', ['$event'])
  onTouchMove(event: TouchEvent) {
    if (!this.currentDragPath || this.isCompleted) return;
    event.preventDefault();
    
    const touch = event.touches[0];
    const element = document.elementFromPoint(touch.clientX, touch.clientY);
    
    if (element && element.classList.contains('grid-cell')) {
      const x = parseInt(element.getAttribute('data-x') || '-1', 10);
      const y = parseInt(element.getAttribute('data-y') || '-1', 10);
      
      if (x >= 0 && y >= 0) {
        const cell = this.grid[y][x];
        this.handleDragOverCell(cell);
      }
    }
  }

  @HostListener('window:touchend')
  onTouchEnd() {
    if (this.currentDragPath) {
      this.moves++;
      this.currentDragPath = null;
      this.checkCompletion();
    }
  }
  
  // Mouse support for desktop testing
  onMouseDown(event: MouseEvent, cell: Cell) {
    if (this.isCompleted) return;
    // Similar to touch start
    if (cell.color) {
      const colorDef = this.levelData?.colors.find(c => c.color === cell.color);
      if (colorDef) {
        this.currentDragPath = colorDef.id;
        if (cell.isEndpoint) {
           this.clearPath(colorDef.id);
           this.addToPath(colorDef.id, cell);
        } else {
           this.truncatePathTo(colorDef.id, cell);
        }
      }
    }
  }
  
  onMouseEnter(cell: Cell) {
    if (this.currentDragPath && !this.isCompleted) {
      this.handleDragOverCell(cell);
    }
  }
  
  @HostListener('window:mouseup')
  onMouseUp() {
    if (this.currentDragPath) {
      this.moves++;
      this.currentDragPath = null;
      this.checkCompletion();
    }
  }

  private handleDragOverCell(cell: Cell) {
    if (!this.currentDragPath) return;
    
    const path = this.paths.get(this.currentDragPath) || [];
    if (path.length === 0) return;
    
    const lastPos = path[path.length - 1];
    
    // Check if same cell
    if (lastPos.x === cell.x && lastPos.y === cell.y) return;
    
    // Check if adjacent
    const isAdjacent = Math.abs(lastPos.x - cell.x) + Math.abs(lastPos.y - cell.y) === 1;
    if (!isAdjacent) return;
    
    // Check if valid move
    const colorDef = this.levelData?.colors.find(c => c.id === this.currentDragPath);
    if (!colorDef) return;
    
    // If moving into an endpoint
    if (cell.isEndpoint) {
      if (cell.endpointId === this.currentDragPath) {
        // Valid completion of path
        this.addToPath(this.currentDragPath, cell);
        this.currentDragPath = null; // stop dragging
        this.moves++;
        this.checkCompletion();
      }
      return; // Can't move into other endpoints
    }
    
    // If moving into our own path, truncate
    const idxInPath = path.findIndex(p => p.x === cell.x && p.y === cell.y);
    if (idxInPath !== -1) {
      this.truncatePathTo(this.currentDragPath, cell);
      return;
    }
    
    // If moving into another color's path, break that path
    if (cell.color && cell.color !== colorDef.color && !cell.isEndpoint) {
       const otherPathId = cell.pathId;
       if (otherPathId) {
          // Truncate the other path just before this cell
          this.truncatePathBefore(otherPathId, cell);
       }
    }
    
    // Add to current path
    this.addToPath(this.currentDragPath, cell);
  }

  private addToPath(pathId: string, cell: Cell) {
    const path = this.paths.get(pathId) || [];
    path.push({x: cell.x, y: cell.y});
    
    const colorDef = this.levelData?.colors.find(c => c.id === pathId);
    if (colorDef) {
      cell.color = colorDef.color;
      if (!cell.isEndpoint) {
        cell.pathId = pathId;
      }
    }
    
    this.updateConnections(pathId);
    this.updateStats();
  }

  private clearPath(pathId: string) {
    const path = this.paths.get(pathId) || [];
    path.forEach(pos => {
      const cell = this.grid[pos.y][pos.x];
      if (!cell.isEndpoint) {
        cell.color = null;
        cell.pathId = undefined;
      }
      cell.connections = { top: false, right: false, bottom: false, left: false };
    });
    this.paths.set(pathId, []);
    this.updateStats();
  }

  private truncatePathTo(pathId: string, cell: Cell) {
    const path = this.paths.get(pathId) || [];
    const idx = path.findIndex(p => p.x === cell.x && p.y === cell.y);
    if (idx !== -1) {
      const removed = path.splice(idx + 1);
      removed.forEach(pos => {
        const c = this.grid[pos.y][pos.x];
        if (!c.isEndpoint) {
          c.color = null;
          c.pathId = undefined;
        }
        c.connections = { top: false, right: false, bottom: false, left: false };
      });
      this.updateConnections(pathId);
      this.updateStats();
    }
  }
  
  private truncatePathBefore(pathId: string, cell: Cell) {
    const path = this.paths.get(pathId) || [];
    const idx = path.findIndex(p => p.x === cell.x && p.y === cell.y);
    if (idx !== -1) {
      const removed = path.splice(idx); // include this cell in removed
      removed.forEach(pos => {
        const c = this.grid[pos.y][pos.x];
        if (!c.isEndpoint) {
          c.color = null;
          c.pathId = undefined;
        }
        c.connections = { top: false, right: false, bottom: false, left: false };
      });
      this.updateConnections(pathId);
      this.updateStats();
    }
  }

  private updateConnections(pathId: string) {
    const path = this.paths.get(pathId) || [];
    // Reset connections for all cells in this path
    path.forEach(pos => {
      this.grid[pos.y][pos.x].connections = { top: false, right: false, bottom: false, left: false };
    });
    
    for (let i = 0; i < path.length - 1; i++) {
      const current = path[i];
      const next = path[i+1];
      
      const currCell = this.grid[current.y][current.x];
      const nextCell = this.grid[next.y][next.x];
      
      if (next.x > current.x) { currCell.connections.right = true; nextCell.connections.left = true; }
      if (next.x < current.x) { currCell.connections.left = true; nextCell.connections.right = true; }
      if (next.y > current.y) { currCell.connections.bottom = true; nextCell.connections.top = true; }
      if (next.y < current.y) { currCell.connections.top = true; nextCell.connections.bottom = true; }
    }
  }

  private updateStats() {
    if (!this.levelData) return;
    
    let completed = 0;
    this.levelData.colors.forEach(c => {
      const path = this.paths.get(c.id) || [];
      if (path.length > 1) {
        const first = path[0];
        const last = path[path.length - 1];
        
        const isFirstEndpoint = this.grid[first.y][first.x].isEndpoint && this.grid[first.y][first.x].endpointId === c.id;
        const isLastEndpoint = this.grid[last.y][last.x].isEndpoint && this.grid[last.y][last.x].endpointId === c.id;
        
        if (isFirstEndpoint && isLastEndpoint) {
          completed++;
        }
      }
    });
    
    this.completedLines = completed;
    
    let filledCells = 0;
    for (let y = 0; y < this.gridSize; y++) {
      for (let x = 0; x < this.gridSize; x++) {
        if (this.grid[y][x].color) {
          filledCells++;
        }
      }
    }
    
    this.fillPercentage = Math.round((filledCells / (this.gridSize * this.gridSize)) * 100);
  }

  private checkCompletion() {
    this.updateStats();
    if (this.completedLines === this.totalLines && this.fillPercentage === 100) {
      this.isCompleted = true;
      if (this.timerInterval) clearInterval(this.timerInterval);
      this.submitCompletion();
    }
  }

  private submitCompletion() {
    
    const serializedPaths: any = {};
    this.paths.forEach((path, key) => {
      serializedPaths[key] = path;
    });
    
    this.gamesService.completeFlowPuzzle(serializedPaths, this.timeElapsed).subscribe({
      next: async (res) => {
        this.alreadyCompletedToday = true;
        
        // Update local profile with new XP and streak
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
        }

        const toast = await this.toastCtrl.create({
          message: res.message + (res.points_awarded > 0 ? ` +${res.points_awarded} XP! Streak: ${res.current_streak}` : ''),
          duration: 3000,
          color: 'success',
          position: 'top'
        });
        toast.present();
      }
    });
  }
}
