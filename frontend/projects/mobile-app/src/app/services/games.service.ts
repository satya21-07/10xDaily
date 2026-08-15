import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

export interface FlowLevel {
  grid_size: number;
  colors: Array<{
    id: string;
    color: string;
    start: [number, number];
    end: [number, number];
    solution_path?: [number, number][];
  }>;
}

export interface TodayFlowResponse {
  completed: boolean;
  date: string;
  level: FlowLevel;
  game_streak: number;
  saved_paths?: any;
  time_taken?: number;
}

export interface CompleteFlowResponse {
  message: string;
  points_awarded: number;
  new_xp: number;
  current_streak: number;
  game_streak?: number;
}

export interface WordSearchLevel {
  grid: string[][];
  words: string[];
  solution: any[];
}

export interface TodayWordSearchResponse {
  completed: boolean;
  date: string;
  level: WordSearchLevel;
  game_streak: number;
  saved_state?: any;
}

export interface MiniSudokuLevel {
  grid: number[][];
  solution: number[][];
}

export interface TodayMiniSudokuResponse {
  completed: boolean;
  date: string;
  level: MiniSudokuLevel;
  game_streak: number;
  saved_state?: any;
}

@Injectable({
  providedIn: 'root'
})
export class GamesService {
  private http = inject(HttpClient);
  private apiUrl = `${environment.apiUrl}/games`;

  getTodayFlowPuzzle(): Observable<TodayFlowResponse> {
    return this.http.get<TodayFlowResponse>(`${this.apiUrl}/flow/today`);
  }

  completeFlowPuzzle(paths: any, timeTaken: number): Observable<CompleteFlowResponse> {
    return this.http.post<CompleteFlowResponse>(`${this.apiUrl}/flow/complete`, { paths, time_taken: timeTaken });
  }

  getTodayWordSearch(): Observable<TodayWordSearchResponse> {
    return this.http.get<TodayWordSearchResponse>(`${this.apiUrl}/word-search/today`);
  }

  completeWordSearch(timeTaken: number, foundWords: string[]): Observable<CompleteFlowResponse> {
    return this.http.post<CompleteFlowResponse>(`${this.apiUrl}/word-search/complete`, { time_taken: timeTaken, found_words: foundWords });
  }

  getTodayMiniSudoku(): Observable<TodayMiniSudokuResponse> {
    return this.http.get<TodayMiniSudokuResponse>(`${this.apiUrl}/mini-sudoku/today`);
  }

  completeMiniSudoku(timeTaken: number, grid: number[][]): Observable<CompleteFlowResponse> {
    return this.http.post<CompleteFlowResponse>(`${this.apiUrl}/mini-sudoku/complete`, { time_taken: timeTaken, grid: grid });
  }
}
