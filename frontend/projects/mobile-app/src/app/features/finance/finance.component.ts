import { Component, OnInit, inject } from '@angular/core';
import { IonicModule } from '@ionic/angular';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { FinanceService, FinanceLesson } from '../../services/finance.service';
import { addIcons } from 'ionicons';
import { arrowBack, walletOutline, trendingUpOutline, cashOutline, chevronDownOutline, chevronUpOutline, bookmarkOutline, bookmark } from 'ionicons/icons';
import { LoaderComponent } from '../../shared/components/loader/loader.component';
import { ProgressService } from '../../services/progress.service';
import { BookmarkService, Bookmark } from '../../core/services/bookmark.service';

@Component({
  selector: 'app-finance',
  standalone: true,
  imports: [IonicModule, CommonModule, RouterLink, LoaderComponent],
  templateUrl: './finance.component.html',
  styleUrls: ['./finance.component.scss'],
  host: { 'class': 'ion-page' }
})
export class FinanceComponent implements OnInit {
  private financeService = inject(FinanceService);
  private progressService = inject(ProgressService);
  private bookmarkService = inject(BookmarkService);
  
  lesson?: FinanceLesson;
  savedBookmarks: Bookmark[] = [];
  isLoading = true;
  expandedConceptIndex = 0;

  constructor() {
    addIcons({ arrowBack, walletOutline, trendingUpOutline, cashOutline, chevronDownOutline, chevronUpOutline, bookmarkOutline, bookmark });
  }

  ngOnInit() {
    this.progressService.markVisited('finance');
    this.loadLesson();
    this.loadBookmarks();
  }

  ionViewWillEnter() {
    this.loadBookmarks();
  }

  loadBookmarks() {
    this.bookmarkService.getBookmarks().subscribe(data => {
      this.savedBookmarks = data.filter(b => b.content_type === 'finance');
    });
  }

  isSaved(concept: any): boolean {
    return this.savedBookmarks.some(b => b.title === concept.title);
  }

  toggleSaveConcept(concept: any, event: Event) {
    event.stopPropagation();
    const existing = this.savedBookmarks.find(b => b.title === concept.title);
    
    if (existing && existing.id) {
      this.bookmarkService.deleteBookmark(existing.id).subscribe(() => {
        this.loadBookmarks();
      });
    } else {
      this.bookmarkService.saveBookmark({
        title: concept.title,
        content_type: 'finance',
        url: concept.explanation,
        details: JSON.stringify(concept)
      }).subscribe(() => {
        this.loadBookmarks();
      });
    }
  }

  loadLesson(event?: any) {
    this.isLoading = true;
    this.financeService.getDailyLesson().subscribe({
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

  toggleConcept(index: number) {
    this.expandedConceptIndex = this.expandedConceptIndex === index ? -1 : index;
  }
}
