import { Injectable, inject } from '@angular/core';
import { AuthService } from './auth.service';
import { HttpClient } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { catchError, tap, map } from 'rxjs/operators';
import { VocabularyWord, DailyVocabularyResponse } from '../models/vocabulary.model';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class VocabularyService {
  private http = inject(HttpClient);
  private authService = inject(AuthService);
  private currentUserId: string | number | null = null;
  private apiUrl = `${environment.apiUrl}/vocabulary`;
  
  private cachedDailyWords: VocabularyWord[] | null = null;
  private cacheDate: string | null = null;


  constructor() {
    this.authService.currentUser$.subscribe(user => {
      const newUserId = user?.id || null;
      if (this.currentUserId !== newUserId) {
        this.currentUserId = newUserId;
        this.cachedDailyWords = null;
        this.cacheDate = null;
      }
    });
  }
  getDailyVocabulary(): Observable<VocabularyWord[]> {
    const today = new Date().toISOString().split('T')[0];
    
    if (this.cachedDailyWords && this.cacheDate === today) {
      return of(JSON.parse(JSON.stringify(this.cachedDailyWords)));
    }
    
    return this.http.get<DailyVocabularyResponse>(`${this.apiUrl}/daily`).pipe(
      map(response => response.words),
      tap(words => {
        this.cachedDailyWords = words;
        this.cacheDate = today;
      }),
      catchError(error => {
        console.error('Error fetching vocabulary, using offline fallback', error);
        return of(this.getOfflineMockData());
      })
    );
  }

  private getOfflineMockData(): VocabularyWord[] {
    return [
      {
        id: 1,
        word: 'Ephemeral',
        meaning: 'Lasting for a very short time.',
        pronunciation: 'ih-FEM-er-uhl',
        example: 'Fashions are ephemeral.',
        difficulty: 'Medium',
        synonyms: ['fleeting', 'passing', 'short-lived'],
        origin: 'From Greek ephēmeros, from epi- + hēmera "day"'
      },
      {
        id: 2,
        word: 'Ubiquitous',
        meaning: 'Present, appearing, or found everywhere.',
        pronunciation: 'yoo-BIK-wi-tuhs',
        example: 'His ubiquitous influence was felt by all the family.',
        difficulty: 'Hard',
        synonyms: ['omnipresent', 'everywhere', 'all-over'],
        origin: 'From Latin ubique "everywhere"'
      }
    ];
  }
}
