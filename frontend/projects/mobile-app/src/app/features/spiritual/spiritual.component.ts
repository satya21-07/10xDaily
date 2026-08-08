import { Component, OnInit, inject } from '@angular/core';
import { IonicModule } from '@ionic/angular';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { SpiritualService, SpiritualLesson } from '../../services/spiritual.service';
import { addIcons } from 'ionicons';
import { arrowBack, medkitOutline, flowerOutline, bookOutline, book, chevronDownOutline, chevronUpOutline, bookmarkOutline, bookmark } from 'ionicons/icons';
import { LoaderComponent } from '../../shared/components/loader/loader.component';
import { ProgressService } from '../../services/progress.service';
import { BookmarkService, Bookmark } from '../../core/services/bookmark.service';

@Component({
  selector: 'app-spiritual',
  standalone: true,
  imports: [IonicModule, CommonModule, RouterLink, LoaderComponent],
  templateUrl: './spiritual.component.html',
  styleUrls: ['./spiritual.component.scss'],
  host: { 'class': 'ion-page' }
})
export class SpiritualComponent implements OnInit {
  private spiritualService = inject(SpiritualService);
  private progressService = inject(ProgressService);
  private bookmarkService = inject(BookmarkService);
  
  lesson?: SpiritualLesson;
  savedBookmarks: Bookmark[] = [];
  isLoading = true;
  expandedLearningIndex = 0;

  constructor() {
    addIcons({ arrowBack, medkitOutline, flowerOutline, bookOutline, book, chevronDownOutline, chevronUpOutline, bookmarkOutline, bookmark });
  }

  ngOnInit() {
    this.progressService.markVisited('spiritual');
    this.loadLesson();
    this.loadBookmarks();
  }

  ionViewWillEnter() {
    this.loadBookmarks();
  }

  loadBookmarks() {
    this.bookmarkService.getBookmarks().subscribe(data => {
      this.savedBookmarks = data.filter(b => b.content_type === 'spiritual');
    });
  }

  isSaved(learning: any): boolean {
    return this.savedBookmarks.some(b => b.title === learning.title);
  }

  toggleSaveLearning(learning: any, event: Event) {
    event.stopPropagation();
    const existing = this.savedBookmarks.find(b => b.title === learning.title);
    
    if (existing && existing.id) {
      this.bookmarkService.deleteBookmark(existing.id).subscribe(() => {
        this.loadBookmarks();
      });
    } else {
      this.bookmarkService.saveBookmark({
        title: learning.title,
        content_type: 'spiritual',
        url: learning.description,
        details: JSON.stringify(learning)
      }).subscribe(() => {
        this.loadBookmarks();
      });
    }
  }

  loadLesson(event?: any) {
    this.isLoading = true;
    this.spiritualService.getDailyLesson().subscribe({
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

  toggleLearning(index: number) {
    this.expandedLearningIndex = this.expandedLearningIndex === index ? -1 : index;
  }
}
