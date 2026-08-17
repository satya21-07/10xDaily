import { Component, OnInit, inject } from '@angular/core';
import { IonicModule } from '@ionic/angular';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { SpiritualService, SpiritualLesson } from '../../services/spiritual.service';
import { addIcons } from 'ionicons';
import {
  arrowBack, bookOutline, book, bookmarkOutline, bookmark,
  chevronForwardOutline, chevronBackOutline, pencilOutline
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
export class SpiritualComponent implements OnInit {
  private spiritualService = inject(SpiritualService);
  private progressService = inject(ProgressService);
  private bookmarkService = inject(BookmarkService);
  private authService = inject(AuthService);

  private currentUserId: number | string = 'guest';

  lesson?: SpiritualLesson;
  savedBookmarks: Bookmark[] = [];
  isLoading = true;
  journalText = '';
  isLessonSaved = false;

  constructor() {
    addIcons({
      arrowBack, bookOutline, book, bookmarkOutline, bookmark,
      chevronForwardOutline, chevronBackOutline, pencilOutline
    });
  }

  ngOnInit() {
    this.authService.currentUser$.subscribe(user => {
      const newUserId = user?.id || 'guest';
      if (this.currentUserId !== newUserId) {
        this.currentUserId = newUserId;
        this.resetState();
      }
      this.loadData();
    });
  }

  private loadData() {
    this.progressService.markVisited('spiritual');
    this.loadLesson();
    this.loadBookmarks();
  }

  private resetState() {
    this.journalText = '';
  }

  ionViewWillEnter() {
    this.loadBookmarks();
  }

  loadBookmarks() {
    this.bookmarkService.getBookmarks(true).subscribe(data => {
      this.savedBookmarks = (data || []).filter(b => b.content_type === 'spiritual');
      this.isLessonSaved = this.lesson
        ? this.savedBookmarks.some(b => b.title === this.lesson?.topic)
        : false;
    });
  }

  toggleSaveLesson(event: Event) {
    event.stopPropagation();
    if (!this.lesson) return;
    const existing = this.savedBookmarks.find(b => b.title === this.lesson?.topic);
    if (existing && existing.id) {
      this.bookmarkService.deleteBookmark(existing.id).subscribe(() => this.loadBookmarks());
    } else {
      this.bookmarkService.saveBookmark({
        title: this.lesson.topic,
        content_type: 'spiritual',
        url: this.lesson.source?.reference || '',
        details: JSON.stringify(this.lesson)
      }).subscribe(() => this.loadBookmarks());
    }
  }

  loadLesson(event?: any) {
    this.isLoading = true;
    this.spiritualService.getDailyLesson().subscribe({
      next: (data) => {
        this.lesson = data;
        this.isLoading = false;
        if (event) event.target.complete();
        this.loadBookmarks();
      },
      error: () => {
        this.isLoading = false;
        if (event) event.target.complete();
      }
    });
  }

  /** Returns the passage text to display in the blockquote */
  get passageText(): string {
    return this.lesson?.source?.translation ?? '';
  }

  /** One-line source attribution e.g. "Bhagavad Gita · Chapter 3, Verse 19" */
  get sourceDisplay(): string {
    if (!this.lesson?.source) return '';
    const { name, chapter, verse, section } = this.lesson.source;
    if (chapter != null && verse != null) {
      return `${name} · Chapter ${chapter}, Verse ${verse}`;
    }
    if (section) return `${name} · ${section}`;
    return `${name} · ${this.lesson.source.reference}`;
  }

  /** Short chapter/verse label e.g. "Chapter 3 · Verse 19" or "Sundara Kanda" */
  get sourceSubtitle(): string {
    if (!this.lesson?.source) return '';
    const { chapter, verse, section } = this.lesson.source;
    if (chapter != null && verse != null) {
      return `Chapter ${chapter} · Verse ${verse}`;
    }
    return section ?? this.lesson.source.reference;
  }

  /** Formatted date string */
  get formattedDate(): string {
    if (!this.lesson?.lesson_date) return '';
    const date = new Date(this.lesson.lesson_date + 'T00:00:00');
    return date.toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
  }

  /** Explanation paragraphs split on double newline or single newline for display */
  get explanationParagraphs(): string[] {
    const text = this.lesson?.reflection?.explanation ?? '';
    // Split on double newlines first, then single if only one paragraph
    const parts = text.split(/\n\n+/).filter(p => p.trim().length > 0);
    return parts.length > 1 ? parts : [text];
  }
}
