import { Component, OnInit, inject } from '@angular/core';
import { IonicModule } from '@ionic/angular';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { HealthService, HealthLesson } from '../../services/health.service';
import { addIcons } from 'ionicons';
import { arrowBack, fitnessOutline, restaurantOutline, barbellOutline, waterOutline, chevronDownOutline, chevronUpOutline, bookmarkOutline, bookmark } from 'ionicons/icons';
import { LoaderComponent } from '../../shared/components/loader/loader.component';
import { ProgressService } from '../../services/progress.service';
import { BookmarkService, Bookmark } from '../../core/services/bookmark.service';

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
  
  lesson?: HealthLesson;
  savedBookmarks: Bookmark[] = [];
  isLoading = true;
  expandedFactIndex: number | null = 0;

  constructor() {
    addIcons({ arrowBack, fitnessOutline, restaurantOutline, barbellOutline, waterOutline, chevronDownOutline, chevronUpOutline, bookmarkOutline, bookmark });
  }

  ngOnInit() {
    this.progressService.markVisited('health');
    this.loadLesson();
    this.loadBookmarks();
  }

  ionViewWillEnter() {
    this.loadBookmarks();
  }

  loadBookmarks() {
    this.bookmarkService.getBookmarks().subscribe(data => {
      this.savedBookmarks = data.filter(b => b.content_type === 'health');
    });
  }

  isSaved(fact: any): boolean {
    return this.savedBookmarks.some(b => b.title === fact.title);
  }

  toggleSaveFact(fact: any, event: Event) {
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
        url: fact.description,
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
        if (event) {
          event.target.complete();
        }
      },
      error: () => {
        this.isLoading = false;
        if (event) {
          event.target.complete();
        }
      }
    });
  }

  toggleFact(index: number) {
    this.expandedFactIndex = this.expandedFactIndex === index ? -1 : index;
  }
}
