import { Component, OnInit, inject } from '@angular/core';
import { IonicModule } from '@ionic/angular';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { HealthService, HealthLesson, HealthFact } from '../../services/health.service';
import { addIcons } from 'ionicons';
import {
  arrowBack, fitnessOutline, restaurantOutline, barbellOutline, waterOutline,
  chevronDownOutline, chevronUpOutline, bookmarkOutline, bookmark, bodyOutline,
  leafOutline, timeOutline, checkmarkCircleOutline, informationCircleOutline,
  documentTextOutline, openOutline, bedOutline, pulseOutline, heartOutline, nutritionOutline,searchOutline, personCircleOutline, checkmark
} from 'ionicons/icons';
import { LoaderComponent } from '../../shared/components/loader/loader.component';
import { ProgressService } from '../../services/progress.service';
import { BookmarkService, Bookmark } from '../../core/services/bookmark.service';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-health',
  standalone: true,
  imports: [IonicModule, CommonModule, RouterLink, LoaderComponent],
  templateUrl: './health.component.html',
  styleUrls: ['./health.component.scss'],
  host: { 'class': 'ion-page' }
})
export class HealthComponent implements OnInit {
  private healthService = inject(HealthService);
  private progressService = inject(ProgressService);
  private bookmarkService = inject(BookmarkService);
  private authService = inject(AuthService);

  private currentUserId: number | string = 'guest';

  lesson?: HealthLesson;
  savedBookmarks: Bookmark[] = [];
  isLoading = true;
  expandedExerciseIndex: number | null = null;

  factIcons = ['pulse-outline', 'time-outline', 'heart-outline', 'nutrition-outline'];

  constructor() {
    addIcons({
      arrowBack, fitnessOutline, restaurantOutline, barbellOutline, waterOutline,
      chevronDownOutline, chevronUpOutline, bookmarkOutline, bookmark, bodyOutline,
      leafOutline, timeOutline, checkmarkCircleOutline, informationCircleOutline,
      documentTextOutline, openOutline, bedOutline, pulseOutline, heartOutline, nutritionOutline,searchOutline, personCircleOutline, checkmark
    });
  }

  ngOnInit() {
    this.authService.currentUser$.subscribe(user => {
      if (!user) return;
      const newUserId = user.id ?? 'guest';
      if (this.currentUserId !== newUserId) {
        this.currentUserId = newUserId;
        this.resetState();
      }
      this.loadData();
    });
  }

  private loadData() {
    this.progressService.markVisited('health');
    this.loadLesson();
    this.loadBookmarks();
  }

  private resetState() {
    this.expandedExerciseIndex = null;
  }

  ionViewWillEnter() {
    this.loadBookmarks();
  }

  loadBookmarks() {
    this.bookmarkService.getBookmarks(true).subscribe(data => {
      this.savedBookmarks = (data || []).filter(b => b.content_type === 'health');
    });
  }

  isSaved(fact: HealthFact): boolean {
    return this.savedBookmarks.some(b => b.title === fact.title);
  }

  toggleSaveFact(fact: HealthFact, event: Event) {
    event.stopPropagation();
    const existing = this.savedBookmarks.find(b => b.title === fact.title);

    if (existing && existing.id) {
      this.bookmarkService.deleteBookmark(existing.id).subscribe(() => {
        this.loadBookmarks();
      });
    } else {
      this.bookmarkService.saveBookmark({
        title: fact.title,
        content_type: 'health',
        url: fact.explanation || '',
        details: JSON.stringify(fact)
      }).subscribe(() => {
        this.loadBookmarks();
      });
    }
  }

  loadLesson(event?: any) {
    this.isLoading = true;
    this.healthService.getDailyLesson().subscribe({
      next: (data) => {
        this.lesson = data;
        this.isLoading = false;
        if (event) { event.target.complete(); }
      },
      error: () => {
        this.isLoading = false;
        if (event) { event.target.complete(); }
      }
    });
  }

  toggleExercise(index: number) {
    this.expandedExerciseIndex = this.expandedExerciseIndex === index ? null : index;
  }

  markCompleted() {
    this.progressService.markVisited('health');
  }

  formatMacro(value: any): string {
    if (value === undefined || value === null) return '-';
    if (typeof value === 'number') {
      return (Math.round(value * 100) / 100).toString();
    }
    if (typeof value === 'string') {
      const match = value.match(/^([\d.]+)\s*(.*)$/);
      if (match) {
        const num = parseFloat(match[1]);
        const unit = match[2];
        if (!isNaN(num)) {
          const formattedNum = Math.round(num * 100) / 100;
          return unit ? `${formattedNum}${unit}` : `${formattedNum}`;
        }
      }
    }
    return String(value);
  }

  toggleHabit(habitTitle: string) {
    this.progressService.toggleHabit(habitTitle);
  }

  isHabitCompleted(habitTitle: string): boolean {
    return this.progressService.isHabitCompleted(habitTitle);
  }
}
