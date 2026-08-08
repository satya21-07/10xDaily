import { Component, OnInit, OnDestroy, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { IonicModule } from '@ionic/angular';
import { VocabularyService } from '../../services/vocabulary.service';
import { VocabularyWord } from '../../models/vocabulary.model';
import { addIcons } from 'ionicons';
import { volumeHighOutline, chevronForward, chevronBack, bookmarkOutline, bookmark, bookOutline, chatbubbleEllipsesOutline, layersOutline, contrastOutline, chevronBackOutline } from 'ionicons/icons';
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
  openAccordions: string[] = [];
  savedBookmarks: Bookmark[] = [];
  isLoading = true;
  
  private viewedWords = new Set<string>();
  private observer: IntersectionObserver | null = null;

  constructor() {
    addIcons({ volumeHighOutline, chevronForward, chevronBack, bookmarkOutline, bookmark, bookOutline, chatbubbleEllipsesOutline, layersOutline, contrastOutline, chevronBackOutline });
  }

  ngOnInit() {
    this.progressService.markVisited('vocabulary');
    this.isLoading = true;
    this.vocabularyService.getDailyVocabulary().subscribe({
      next: (data) => {
        this.words = data;
        this.openAccordions = this.words.map((_, i) => i.toString());
        this.isLoading = false;
        
        // Setup tracking after the DOM updates with the loaded words
        setTimeout(() => {
          // Fallback: The first two words are always visible on load
          if (this.words.length > 0) this.viewedWords.add(this.words[0].word);
          if (this.words.length > 1) this.viewedWords.add(this.words[1].word);
          
          this.setupScrollTracking();
        }, 100);
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
    if (this.observer) {
      this.observer.disconnect();
    }
    
    if (this.viewedWords.size > 0 && this.authService.isLoggedIn) {
      this.authService.updateStats({ words_learned_increment: this.viewedWords.size }).subscribe();
      this.viewedWords.clear();
    }
  }

  private setupScrollTracking() {
    if (typeof window === 'undefined' || !('IntersectionObserver' in window)) return;
    
    this.observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const word = entry.target.getAttribute('data-word');
          if (word) {
            this.viewedWords.add(word);
          }
        }
      });
    }, { threshold: 0.01 }); // 1% visible triggers it

    // We need to wait for Ionic Web Components to fully hydrate and render
    setTimeout(() => {
      const elements = document.querySelectorAll('.word-card-container');
      elements.forEach(el => this.observer?.observe(el));
    }, 500);
  }

  ionViewWillEnter() {
    this.loadBookmarks();
  }

  loadBookmarks() {
    this.bookmarkService.getBookmarks().subscribe(data => {
      this.savedBookmarks = data.filter(b => b.content_type === 'vocabulary');
    });
  }

  isSaved(word: VocabularyWord): boolean {
    return this.savedBookmarks.some(b => b.title === word.word);
  }

  toggleSaveWord(word: VocabularyWord, event: Event) {
    event.stopPropagation();
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

  playAudio(word: VocabularyWord, event: Event) {
    event.stopPropagation();
    
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
      utterance.rate = 0.85; // Slightly slower for clearer enunciation
      window.speechSynthesis.speak(utterance);
    } else {
      console.warn("Text-to-speech not supported in this browser.");
    }
  }
}
