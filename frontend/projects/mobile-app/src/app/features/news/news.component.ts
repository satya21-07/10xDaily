import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { IonicModule } from '@ionic/angular';
import { NewsService } from '../../services/news.service';
import { NewsArticle } from '../../models/news.model';
import { addIcons } from 'ionicons';
import { shareOutline, bookmarkOutline, bookmark, openOutline, arrowBack } from 'ionicons/icons';
import { RouterLink } from '@angular/router';
import { LoaderComponent } from '../../shared/components/loader/loader.component';
import { ProgressService } from '../../services/progress.service';
import { BookmarkService, Bookmark } from '../../core/services/bookmark.service';

@Component({
  selector: 'app-news',
  standalone: true,
  imports: [IonicModule, CommonModule, RouterLink, LoaderComponent],
  templateUrl: './news.component.html',
  styleUrls: ['./news.component.scss'],
  host: { 'class': 'ion-page' }
})
export class NewsComponent implements OnInit {
  private newsService = inject(NewsService);
  private progressService = inject(ProgressService);
  private bookmarkService = inject(BookmarkService);
  
  articles: NewsArticle[] = [];
  savedBookmarks: Bookmark[] = [];
  isLoading = true;
  segment: string = 'india';

  constructor() {
    addIcons({ shareOutline, bookmarkOutline, bookmark, openOutline, arrowBack });
  }

  ngOnInit() {
    this.progressService.markVisited('news');
    this.loadNews();
    this.loadBookmarks();
  }

  ionViewWillEnter() {
    this.loadBookmarks();
  }

  loadBookmarks() {
    this.bookmarkService.getBookmarks().subscribe(data => {
      this.savedBookmarks = data.filter(b => b.content_type === 'news');
    });
  }

  isSaved(article: NewsArticle): boolean {
    return this.savedBookmarks.some(b => b.title === article.title);
  }

  toggleSaveArticle(article: NewsArticle, event: Event) {
    event.stopPropagation();
    const existing = this.savedBookmarks.find(b => b.title === article.title);
    
    if (existing && existing.id) {
      this.bookmarkService.deleteBookmark(existing.id).subscribe(() => {
        this.loadBookmarks();
      });
    } else {
      this.bookmarkService.saveBookmark({
        title: article.title,
        content_type: 'news',
        url: article.url,
        details: JSON.stringify(article)
      }).subscribe(() => {
        this.loadBookmarks();
      });
    }
  }

  loadNews(event?: any) {
    this.isLoading = true;
    this.newsService.getNews(this.segment).subscribe({
      next: (data) => {
        this.articles = data;
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

  segmentChanged(event: any) {
    this.segment = event.detail.value;
    this.loadNews();
  }

  openUrl(url: string) {
    if (url) {
      window.open(url, '_blank');
    }
  }
}
