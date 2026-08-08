import { Component, OnInit, OnDestroy, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { IonicModule } from '@ionic/angular';
import { VocabularyService } from '../../services/vocabulary.service';
import { VocabularyWord } from '../../models/vocabulary.model';
import { addIcons } from 'ionicons';
import { volumeHighOutline, chevronForwardOutline, chevronBack, bookmarkOutline, bookmark, bookOutline, chatbubbleEllipsesOutline, layersOutline, contrastOutline, chevronBackOutline, shareSocialOutline, checkmarkOutline, chevronDownOutline, thumbsUpOutline, thumbsUp } from 'ionicons/icons';
import { RouterLink } from '@angular/router';
import { ProgressService } from '../../services/progress.service';
import { BookmarkService, Bookmark } from '../../core/services/bookmark.service';
import { AuthService } from '../../services/auth.service';
import { LoaderComponent } from '../../shared/components/loader/loader.component';

@Component({
  selector: 'app-vocabulary',
  standalone: true,
  imports: [IonicModule, CommonModule, RouterLink, LoaderComponent],
  templateUrl: './vocabulary.component.html',
  styleUrls: ['./vocabulary.component.scss'],
  host: { 'class': 'ion-page' }
})
export class VocabularyComponent implements OnInit, OnDestroy {
  private vocabularyService = inject(VocabularyService);
  private progressService = inject(ProgressService);
  private bookmarkService = inject(BookmarkService);
  private authService = inject(AuthService);
  
  words: VocabularyWord[] = [];
  currentIndex: number = 0;
  savedBookmarks: Bookmark[] = [];
  isLoading = true;
  
  private sessionViewedWords = new Set<string>();

  private getTodayDateKey(): string {
    const today = new Date();
    return `viewedWords_${today.getFullYear()}-${today.getMonth() + 1}-${today.getDate()}`;
  }

  private getStoredViewedWords(): Set<string> {
    const key = this.getTodayDateKey();
    const stored = localStorage.getItem(key);
    if (stored) {
      try {
        return new Set(JSON.parse(stored));
      } catch (e) {
        return new Set();
      }
    }
    return new Set();
  }

  private saveStoredViewedWords(words: Set<string>) {
    const key = this.getTodayDateKey();
    localStorage.setItem(key, JSON.stringify(Array.from(words)));
  }

  constructor() {
    addIcons({ volumeHighOutline, chevronForwardOutline, chevronBack, bookmarkOutline, bookmark, bookOutline, chatbubbleEllipsesOutline, layersOutline, contrastOutline, chevronBackOutline, shareSocialOutline, checkmarkOutline, chevronDownOutline, thumbsUpOutline, thumbsUp });
  }

  ngOnInit() {
    this.progressService.markVisited('vocabulary');
    this.isLoading = true;
    this.vocabularyService.getDailyVocabulary().subscribe({
      next: (data) => {
        this.words = data;
        this.currentIndex = 0;
        this.isLoading = false;
        
        if (this.words.length > 0) {
          const todayWords = this.getStoredViewedWords();
          if (!todayWords.has(this.words[0].word)) {
            this.sessionViewedWords.add(this.words[0].word);
          }
        }
      },
      error: () => {
        this.isLoading = false;
      }
    });
    this.loadBookmarks();
  }

  ionViewWillLeave() {
    this.syncWords();
  }
  
  ngOnDestroy() {
    this.syncWords();
  }
  
  private syncWords() {
    if (this.sessionViewedWords.size > 0 && this.authService.isLoggedIn) {
      this.authService.updateStats({ words_learned_increment: this.sessionViewedWords.size }).subscribe();
      
      const todayWords = this.getStoredViewedWords();
      this.sessionViewedWords.forEach(w => todayWords.add(w));
      this.saveStoredViewedWords(todayWords);
      
      this.sessionViewedWords.clear();
    }
  }

  ionViewWillEnter() {
    this.loadBookmarks();
  }

  get currentWord(): VocabularyWord | null {
    if (this.words.length === 0) return null;
    return this.words[this.currentIndex];
  }

  get previousWord(): VocabularyWord | null {
    if (this.currentIndex > 0) {
      return this.words[this.currentIndex - 1];
    }
    return null;
  }

  get nextWord(): VocabularyWord | null {
    if (this.currentIndex < this.words.length - 1) {
      return this.words[this.currentIndex + 1];
    }
    return null;
  }

  next() {
    if (this.currentIndex < this.words.length - 1) {
      this.currentIndex++;
      if (this.currentWord) {
        const todayWords = this.getStoredViewedWords();
        if (!todayWords.has(this.currentWord.word)) {
          this.sessionViewedWords.add(this.currentWord.word);
        }
      }
    }
  }

  previous() {
    if (this.currentIndex > 0) {
      this.currentIndex--;
    }
  }

  loadBookmarks() {
    this.bookmarkService.getBookmarks().subscribe(data => {
      this.savedBookmarks = data.filter(b => b.content_type === 'vocabulary');
    });
  }

  isSaved(word: VocabularyWord): boolean {
    return this.savedBookmarks.some(b => b.title === word.word);
  }

  toggleSaveWord(word: VocabularyWord, event?: Event) {
    if (event) event.stopPropagation();
    const existing = this.savedBookmarks.find(b => b.title === word.word);
    
    if (existing && existing.id) {
      this.bookmarkService.deleteBookmark(existing.id).subscribe(() => {
        this.loadBookmarks();
      });
    } else {
      this.bookmarkService.saveBookmark({
        title: word.word,
        content_type: 'vocabulary',
        url: word.meaning,
        details: JSON.stringify(word)
      }).subscribe(() => {
        this.loadBookmarks();
      });
    }
  }
  
  toggleLearned(word: VocabularyWord) {
    word.learned = !word.learned;
  }
  
  shareWord() {
    if (this.currentWord) {
      if (navigator.share) {
        navigator.share({
          title: this.currentWord.word,
          text: `Check out today's vocabulary word: ${this.currentWord.word} - ${this.currentWord.definitions?.[0]?.definition}`,
          url: window.location.href,
        }).catch(console.error);
      } else {
        console.log("Web Share API not supported. Sharing:", this.currentWord.word);
      }
    }
  }

  playAudio(word: VocabularyWord, event?: Event) {
    if (event) event.stopPropagation();
    
    if (word.audio_url) {
       const audio = new Audio(word.audio_url);
       audio.play().catch(e => {
         console.error("Error playing audio url, falling back to TTS:", e);
         this.speakWord(word.word);
       });
    } else {
       this.speakWord(word.word);
    }
  }

  private speakWord(text: string) {
    if ('speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = 'en-US';
      utterance.rate = 0.85; 
      window.speechSynthesis.speak(utterance);
    } else {
      console.warn("Text-to-speech not supported in this browser.");
    }
  }
}
