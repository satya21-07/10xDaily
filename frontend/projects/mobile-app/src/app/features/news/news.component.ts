import { Component, OnInit, inject, ViewChild, ElementRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { IonicModule } from '@ionic/angular';
import { NewsService } from '../../services/news.service';
import { NewsArticle } from '../../models/news.model';
import { addIcons } from 'ionicons';
import { shareOutline, bookmarkOutline, bookmark, openOutline, arrowBack, searchOutline, personCircleOutline, chevronForwardOutline } from 'ionicons/icons';
import { RouterLink } from '@angular/router';
import { LoaderComponent } from '../../shared/components/loader/loader.component';
import { ProgressService } from '../../services/progress.service';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-news',
  standalone: true,
  imports: [IonicModule, CommonModule, RouterLink, LoaderComponent],
  templateUrl: './news.component.html',
  styleUrls: ['./news.component.scss'],
  host: { 'class': 'ion-page' }
})
export class NewsComponent implements OnInit {
  @ViewChild('slider') slider?: ElementRef<HTMLElement>;
  
  private newsService = inject(NewsService);
  private progressService = inject(ProgressService);
  private authService = inject(AuthService);
  
  private currentUserId: number | string = 'guest';
  
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
    this.progressService.markVisited('news');
    this.loadNews();
  }

  private resetState() {
    this.segment = 'for you';
    this.articles = [];
  }

  ionViewWillEnter() {
    this.loadNews();
  }
  
  onScroll(event: Event) {
    const el = event.target as HTMLElement;
    const index = Math.round(el.scrollLeft / el.clientWidth);
    const newSegment = this.categories[index].value;
    
    if (this.segment !== newSegment) {
      this.segment = newSegment;
      this.loadNews();
      this.scrollToActiveTab();
    }
  }

  scrollToActiveTab() {
    setTimeout(() => {
       const activeTab = document.querySelector('.category-tab.active');
       if (activeTab) {
          activeTab.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' });
       }
    }, 50);
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
    
    // Sync slider position with segment change
    const index = this.categories.findIndex(c => c.value === this.segment);
    if (this.slider && this.slider.nativeElement && index !== -1) {
      const el = this.slider.nativeElement;
      el.scrollTo({
        left: el.clientWidth * index,
        behavior: 'smooth'
      });
    }
    
    this.loadNews();
    this.scrollToActiveTab();
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
