import { Component, OnInit, OnDestroy, inject } from '@angular/core';
import { IonicModule, ToastController } from '@ionic/angular';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { SpiritualService, SpiritualLesson } from '../../services/spiritual.service';
import { addIcons } from 'ionicons';
import {
  arrowBack, bookOutline, book, bookmarkOutline, bookmark,
  chevronForwardOutline, chevronBackOutline, chevronDownOutline, chevronUpOutline, pencilOutline,
  volumeHighOutline, volumeMuteOutline, copyOutline, checkmarkOutline,
  refreshOutline, sparklesOutline, bulbOutline, calendarOutline,
  shareSocialOutline, checkmarkCircleOutline, listOutline
} from 'ionicons/icons';
import { LoaderComponent } from '../../shared/components/loader/loader.component';
import { ProgressService } from '../../services/progress.service';
import { BookmarkService, Bookmark } from '../../core/services/bookmark.service';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-spiritual',
  standalone: true,
  imports: [IonicModule, CommonModule, RouterLink, LoaderComponent, FormsModule],
  templateUrl: './spiritual.component.html',
  styleUrls: ['./spiritual.component.scss'],
  host: { 'class': 'ion-page' }
})
export class SpiritualComponent implements OnInit, OnDestroy {
  private spiritualService = inject(SpiritualService);
  private progressService = inject(ProgressService);
  private bookmarkService = inject(BookmarkService);
  private authService = inject(AuthService);
  private toastCtrl = inject(ToastController);

  private currentUserId: number | string = 'guest';

  // Active state
  selectedScripture: 'gita' | 'ramayana' | 'mahabharata' = 'gita';
  lesson?: SpiritualLesson;
  savedBookmarks: Bookmark[] = [];
  isLoading = true;
  journalText = '';
  isLessonSaved = false;
  
  // Customization & Controls
  showTransliteration = false;
  isPlayingAudio = false;
  copiedToast = false;
  journalSaved = false;
  isStoryExpanded = false;


  constructor() {
    addIcons({
      arrowBack, bookOutline, book, bookmarkOutline, bookmark,
      chevronForwardOutline, chevronBackOutline, chevronDownOutline, chevronUpOutline, pencilOutline,
      volumeHighOutline, volumeMuteOutline, copyOutline, checkmarkOutline,
      refreshOutline, sparklesOutline, bulbOutline, calendarOutline,
      shareSocialOutline, checkmarkCircleOutline, listOutline
    });
  }

  toggleStoryAccordion() {
    this.isStoryExpanded = !this.isStoryExpanded;
  }


  ngOnInit() {
    this.initSpeechVoices();
    this.authService.currentUser$.subscribe(user => {
      const newUserId = user?.id || 'guest';
      if (this.currentUserId !== newUserId) {
        this.currentUserId = newUserId;
        this.resetState();
      }
      this.loadData();
    });
  }


  ngOnDestroy() {
    this.stopAudio();
  }

  private loadData() {
    this.progressService.markVisited('spiritual');
    this.loadLesson();
    this.loadBookmarks();
  }

  private resetState() {
    this.journalText = '';
    this.journalSaved = false;
  }

  ionViewWillEnter() {
    this.loadBookmarks();
  }

  ionViewWillLeave() {
    this.stopAudio();
  }

  selectScripture(type: 'gita' | 'ramayana' | 'mahabharata') {
    if (this.selectedScripture === type) return;
    this.stopAudio();
    this.selectedScripture = type;
    this.loadLesson();
  }


  loadLesson(event?: any, day?: number, chapter?: number, verse?: number) {
    this.isLoading = true;
    this.stopAudio();

    this.spiritualService.getDailyLesson(this.selectedScripture, day, chapter, verse).subscribe({
      next: (data) => {
        this.lesson = data;
        this.isLoading = false;
        
        this.loadJournalForCurrentLesson();
        if (event) event.target.complete();
        this.loadBookmarks();
      },
      error: () => {
        this.isLoading = false;
        if (event) event.target.complete();
      }
    });
  }

  selectedMeaningLanguage: 'hindi' | 'english' = 'hindi';

  setMeaningLanguage(lang: 'hindi' | 'english') {
    if (this.selectedMeaningLanguage === lang) return;
    this.stopAudio();
    this.selectedMeaningLanguage = lang;
  }

  toggleTransliteration() {
    this.showTransliteration = !this.showTransliteration;
  }


  availableVoices: SpeechSynthesisVoice[] = [];

  private initSpeechVoices() {
    if ('speechSynthesis' in window) {
      this.availableVoices = window.speechSynthesis.getVoices();
      window.speechSynthesis.onvoiceschanged = () => {
        this.availableVoices = window.speechSynthesis.getVoices();
      };
    }
  }


  audioLanguage: 'hindi' | 'english' | 'sanskrit' = 'hindi';

  // ── Speech Synthesis (Audio Chanting & Recitation) ─────────────────
  toggleChantingAudio(lang: 'hindi' | 'english' | 'sanskrit' = 'hindi') {
    if (this.isPlayingAudio) {
      this.stopAudio();
      return;
    }

    if (!('speechSynthesis' in window) || !this.lesson) {
      this.presentToast('Audio playback not supported on this browser');
      return;
    }

    window.speechSynthesis.cancel();
    window.speechSynthesis.resume();
    this.audioLanguage = lang;

    let rawText = '';
    let targetLang = 'hi-IN';

    // Refresh voices if list was empty
    const voices = this.availableVoices.length > 0 ? this.availableVoices : window.speechSynthesis.getVoices();

    if (lang === 'hindi') {
      const hiVoice = voices.find(v => 
        v.lang.toLowerCase().startsWith('hi') || 
        v.lang.toLowerCase().includes('sa') || 
        v.name.toLowerCase().includes('hindi') || 
        v.name.toLowerCase().includes('kalpana') ||
        v.name.toLowerCase().includes('hemant')
      );

      if (hiVoice) {
        rawText = this.lesson.source.hindi_translation || this.lesson.source.original_sanskrit || this.lesson.source.translation;
        targetLang = 'hi-IN';
      } else {
        // If device has no Hindi voice pack, English TTS chokes on Hindi letters.
        // Fall back to English translation so user gets audio recitation.
        this.presentToast('Hindi voice not installed on device. Reciting in English.');
        rawText = this.lesson.source.translation;
        targetLang = 'en-US';
      }
    } else {
      rawText = this.lesson.source.translation;
      targetLang = 'en-US';
    }

    // Clean and sanitize text to prevent TTS from reading punctuation symbols / danda / footnotes
    const cleanText = this.cleanTextForSpeech(rawText);
    if (!cleanText) {
      this.presentToast('No text available for recitation');
      return;
    }

    const utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.lang = targetLang;

    if (targetLang === 'hi-IN') {
      const hiVoice = voices.find(v => 
        v.lang.toLowerCase().startsWith('hi') || 
        v.lang.toLowerCase().includes('sa') || 
        v.name.toLowerCase().includes('hindi') || 
        v.name.toLowerCase().includes('kalpana') ||
        v.name.toLowerCase().includes('hemant')
      );
      if (hiVoice) utterance.voice = hiVoice;
      utterance.rate = 0.85;
      utterance.pitch = 1.0;
    } else {
      const enVoice = voices.find(v => 
        v.lang.toLowerCase().startsWith('en-in') || 
        v.lang.toLowerCase().startsWith('en-us') || 
        v.lang.toLowerCase().startsWith('en-gb') ||
        v.name.toLowerCase().includes('english')
      );
      if (enVoice) utterance.voice = enVoice;
      utterance.rate = 0.90;
      utterance.pitch = 1.0;
    }

    utterance.onstart = () => {
      this.isPlayingAudio = true;
    };
    utterance.onend = () => {
      this.isPlayingAudio = false;
    };
    utterance.onerror = (err) => {
      console.warn('Speech synthesis error:', err);
      this.isPlayingAudio = false;
    };

    window.speechSynthesis.speak(utterance);
  }

  private cleanTextForSpeech(text: string): string {
    if (!text) return '';
    return text
      .replace(/^[।\|\s]*[०-९0-9\.\-–]+[।\|\s]*/, '') // Strip leading numbers like ।।1.1।। or 1.1
      .replace(/\|+[०-९0-9\-–\s]*\|+/g, ' ')           // Remove verse numbers like ||१-१||
      .replace(/^[०-९0-9\.\s]+/, '')                  // Strip any remaining numbers at start
      .replace(/[\|॥।]/g, ' ')                         // Remove danda characters
      .replace(/\(टिप्पणी[^\)]*\)/g, ' ')              // Remove Hindi commentary footnote tags
      .replace(/\([^\)]*\)/g, ' ')                     // Remove parenthetical text
      .replace(/[\n\r]+/g, '. ')                       // Replace line breaks with clean pauses
      .replace(/\s+/g, ' ')                            // Normalize spaces
      .trim();
  }


  stopAudio() {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
    }
    this.isPlayingAudio = false;
  }


  // ── Copy Verse Card ───────────────────────────────────────────────
  async copyVerseCard() {
    if (!this.lesson) return;
    const src = this.lesson.source;
    const text = `🕉️ ${src.name} — ${src.reference}\n\n` +
      (src.original_sanskrit ? `${src.original_sanskrit}\n\n` : '') +
      (src.transliteration ? `(${src.transliteration})\n\n` : '') +
      `Meaning:\n${src.translation}\n\n` +
      `✨ Daily Takeaway: ${this.lesson.reflection.key_takeaways[0] || ''}\n` +
      `— via 10xDaily Spiritual`;

    try {
      await navigator.clipboard.writeText(text);
      this.copiedToast = true;
      setTimeout(() => (this.copiedToast = false), 2500);
      this.presentToast('Shloka and translation copied to clipboard!');
    } catch {
      this.presentToast('Failed to copy to clipboard');
    }
  }

  // ── Journal Persistence ───────────────────────────────────────────
  saveJournal() {
    if (!this.lesson) return;
    const key = `journal_spiritual_${this.currentUserId}_${this.selectedScripture}_${this.lesson.day_number}`;
    localStorage.setItem(key, this.journalText);
    this.journalSaved = true;
    setTimeout(() => (this.journalSaved = false), 3000);
    this.presentToast('Journal entry saved to your device!');
  }

  private loadJournalForCurrentLesson() {
    if (!this.lesson) return;
    const key = `journal_spiritual_${this.currentUserId}_${this.selectedScripture}_${this.lesson.day_number}`;
    this.journalText = localStorage.getItem(key) || '';
  }

  // ── Bookmarking ───────────────────────────────────────────────────
  loadBookmarks() {
    this.bookmarkService.getBookmarks(true).subscribe(data => {
      this.savedBookmarks = (data || []).filter(b => b.content_type === 'spiritual');
      this.isLessonSaved = this.lesson
        ? this.savedBookmarks.some(b => b.title === this.lesson?.source?.reference || b.title === this.lesson?.topic)
        : false;
    });
  }

  toggleSaveLesson(event: Event) {
    event.stopPropagation();
    if (!this.lesson) return;
    const ref = this.lesson.source.reference;
    const existing = this.savedBookmarks.find(b => b.title === ref || b.title === this.lesson?.topic);
    
    if (existing && existing.id) {
      this.bookmarkService.deleteBookmark(existing.id).subscribe(() => {
        this.loadBookmarks();
        this.presentToast('Removed from saved shlokas');
      });
    } else {
      this.bookmarkService.saveBookmark({
        title: ref,
        content_type: 'spiritual',
        url: ref,
        details: JSON.stringify(this.lesson)
      }).subscribe(() => {
        this.loadBookmarks();
        this.presentToast('Saved to your bookmarks!');
      });
    }
  }

  private async presentToast(message: string) {
    const toast = await this.toastCtrl.create({
      message,
      duration: 2000,
      position: 'bottom',
      cssClass: 'spiritual-toast'
    });
    await toast.present();
  }

  get progressPercentage(): number {
    if (!this.lesson || !this.lesson.total_days_or_verses) return 0;
    return Math.round((this.lesson.day_number / this.lesson.total_days_or_verses) * 100);
  }

  get formattedDate(): string {
    if (!this.lesson?.lesson_date) return '';
    const date = new Date(this.lesson.lesson_date + 'T00:00:00');
    return date.toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
  }
}


