import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { IonicModule } from '@ionic/angular';
import { NewsService } from '../../services/news.service';
import { NewsArticle } from '../../models/news.model';
import { addIcons } from 'ionicons';
import { shareOutline, bookmarkOutline, bookmark, openOutline, arrowBack, searchOutline, personCircleOutline, chevronForwardOutline } from 'ionicons/icons';
import { RouterLink } from '@angular/router';
import { LoaderComponent } from '../../shared/components/loader/loader.component';
import { ProgressService } from '../../services/progress.service';

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
  
  articles: NewsArticle[] = [];
  isLoading = true;
  segment: string = 'for you';
  
  categories = [
    { value: 'for you', label: 'For You' },
    { value: 'india', label: 'India' },
    { value: 'world', label: 'World' },
    { value: 'business', label: 'Business' },
    { value: 'technology', label: 'Technology' },
    { value: 'sports', label: 'Sports' },
    { value: 'entertainment', label: 'Entertainment' },
    { value: 'science', label: 'Science' },
    { value: 'health', label: 'Health' }
  ];

  constructor() {
    addIcons({ shareOutline, bookmarkOutline, bookmark, openOutline, arrowBack, searchOutline, personCircleOutline, chevronForwardOutline });
  }

  ngOnInit() {
    this.progressService.markVisited('news');
    this.loadNews();
  }

  ionViewWillEnter() {
    this.loadNews(); // Refresh to get updated save states if changed elsewhere
  }

  toggleSaveArticle(article: NewsArticle, event: Event) {
    event.stopPropagation();
    
    // Optimistic UI update
    const previousState = article.is_saved;
    article.is_saved = !article.is_saved;
    
    if (!previousState) {
      this.newsService.saveArticle(article).subscribe({
        error: (err) => {
          console.error('Failed to save article', err);
          article.is_saved = false; // Revert on failure
        }
      });
    } else {
      this.newsService.unsaveArticle(article.id, article.url).subscribe({
        error: (err) => {
          console.error('Failed to unsave article', err);
          article.is_saved = true; // Revert on failure
        }
      });
    }
  }

  loadNews(event?: any) {
    if (!event) this.isLoading = true;
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

  openUrl(url: string | undefined) {
    if (url) {
      window.open(url, '_blank');
    }
  }

  handleImageError(event: any) {
    event.target.style.display = 'none';
  }
}
