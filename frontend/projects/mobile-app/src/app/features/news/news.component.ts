import { Component, OnInit, OnDestroy, HostListener, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { IonicModule, ToastController } from '@ionic/angular';
import { NewsService } from '../../services/news.service';
import { NewsArticle } from '../../models/news.model';
import { addIcons } from 'ionicons';
import { 
  shareSocialOutline, 
  bookmarkOutline, 
  bookmark, 
  openOutline, 
  arrowBack, 
  timeOutline, 
  newspaperOutline, 
  personCircleOutline, 
  chevronForwardOutline,
  sparklesOutline,
  refreshOutline,
  globeOutline,
  closeOutline,
  closeCircle,
  linkOutline,
  bookOutline,
  eyeOutline,
  bulbOutline
} from 'ionicons/icons';
import { RouterLink } from '@angular/router';
import { ProgressService } from '../../services/progress.service';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-news',
  standalone: true,
  imports: [IonicModule, CommonModule, RouterLink],
  templateUrl: './news.component.html',
  styleUrls: ['./news.component.scss'],
  host: { 'class': 'ion-page' }
})
export class NewsComponent implements OnInit, OnDestroy {
  private newsService = inject(NewsService);
  private progressService = inject(ProgressService);
  private authService = inject(AuthService);
  private toastCtrl = inject(ToastController);

  // Category Cache: Stores loaded articles per category to avoid re-fetching and flicker
  private articlesCache = new Map<string, NewsArticle[]>();
  
  activeCategory: string = 'for you';
  articles: NewsArticle[] = [];
  isLoading = false;
  imageErrors = new Set<string>();

  // In-App Article Reader State
  selectedArticle: NewsArticle | null = null;
  isReaderOpen: boolean = false;
  isLoadingStory: boolean = false;

  categories = [

    { value: 'for you', label: 'For You', icon: 'newspaper-outline' },
    { value: 'india', label: 'India', icon: 'newspaper-outline' },
    { value: 'world', label: 'World', icon: 'globe-outline' },
    { value: 'business', label: 'Business', icon: 'newspaper-outline' },
    { value: 'technology', label: 'Technology', icon: 'newspaper-outline' },
    { value: 'sports', label: 'Sports', icon: 'newspaper-outline' },
    { value: 'entertainment', label: 'Entertainment', icon: 'newspaper-outline' },
    { value: 'science', label: 'Science', icon: 'newspaper-outline' },
    { value: 'health', label: 'Health', icon: 'newspaper-outline' }
  ];

  constructor() {
    addIcons({ 
      shareSocialOutline, 
      bookmarkOutline, 
      bookmark, 
      openOutline, 
      arrowBack, 
      timeOutline, 
      newspaperOutline, 
      personCircleOutline, 
      chevronForwardOutline,
      sparklesOutline,
      refreshOutline,
      globeOutline,
      closeOutline,
      closeCircle,
      linkOutline,
      bookOutline,
      eyeOutline,
      bulbOutline
    });
  }

  ngOnInit() {
    this.progressService.markVisited('news');
    this.selectCategory(this.activeCategory);
  }

  selectCategory(category: string, forceRefresh = false, refresherEvent?: any) {
    this.activeCategory = category;
    this.scrollToActiveTab();

    // 1. Instant Render from Cache if available
    if (!forceRefresh && this.articlesCache.has(category)) {
      this.articles = this.articlesCache.get(category) || [];
      this.isLoading = false;
      if (refresherEvent) refresherEvent.target.complete();
      return;
    }

    // 2. Fetch if not in cache or user initiated refresh
    if (!refresherEvent) {
      this.articles = [];
      this.isLoading = true;
    }

    this.newsService.getNews(category).subscribe({
      next: (data) => {
        const cleanedData = (data || []).map(item => ({
          ...item,
          summary: this.cleanSummary(item.summary || item.ai_summary || '')
        }));
        this.articlesCache.set(category, cleanedData);
        this.articles = cleanedData;
        this.isLoading = false;
        if (refresherEvent) refresherEvent.target.complete();
      },
      error: (err) => {
        console.error(`Failed to fetch news for category ${category}:`, err);
        this.isLoading = false;
        if (refresherEvent) refresherEvent.target.complete();
      }
    });
  }

  onRefresh(event: any) {
    this.selectCategory(this.activeCategory, true, event);
  }

  scrollToActiveTab() {
    setTimeout(() => {
      const activeTab = document.querySelector('.category-pill.active');
      if (activeTab) {
        activeTab.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' });
      }
    }, 60);
  }

  @HostListener('window:popstate', ['$event'])
  onPopState(event: PopStateEvent) {
    if (this.isReaderOpen) {
      this.isReaderOpen = false;
    }
  }

  ngOnDestroy() {
    if (this.isReaderOpen && window.history.state?.modal === 'news-reader') {
      window.history.back();
    }
  }

  openArticleReader(article: NewsArticle, event?: Event) {
    if (event) {
      event.stopPropagation();
    }
    this.selectedArticle = article;
    this.isReaderOpen = true;

    // Push browser history state so mousepad/swipe-back or browser Back closes modal instead of exiting news
    if (window.history.state?.modal !== 'news-reader') {
      window.history.pushState({ modal: 'news-reader' }, '', window.location.href);
    }

    // Fetch full comprehensive story if not already cached
    if (!article.content || article.content.length < 200 || !article.key_highlights || article.key_highlights.length === 0) {
      this.isLoadingStory = true;
      this.newsService.getFullStory(article.url, article.title, article.summary, article.source, article.category || this.activeCategory).subscribe({
        next: (res) => {
          if (res) {
            article.content = res.content || article.content;
            if (res.summary && res.summary.length > (article.summary ? article.summary.length : 0)) {
              article.summary = res.summary;
            }
            article.key_highlights = res.key_highlights || article.key_highlights;
            article.full_coverage = res.full_coverage || article.full_coverage;
            article.why_it_matters = res.why_it_matters || article.why_it_matters;
            
            if (this.selectedArticle && this.selectedArticle.id === article.id) {
              this.selectedArticle = { ...article };
            }
          }
          this.isLoadingStory = false;
        },
        error: () => {
          this.isLoadingStory = false;
        }
      });
    }
  }

  closeArticleReader() {
    if (this.isReaderOpen) {
      this.isReaderOpen = false;
      if (window.history.state?.modal === 'news-reader') {
        window.history.back();
      }
    }
  }

  toggleSaveArticle(article: NewsArticle, event: Event) {
    event.stopPropagation();
    
    const previousState = article.is_saved;
    article.is_saved = !article.is_saved;
    
    if (!previousState) {
      this.newsService.saveArticle(article).subscribe({
        next: async () => {
          const toast = await this.toastCtrl.create({
            message: 'Article saved to bookmarks',
            duration: 1500,
            position: 'bottom',
            color: 'dark'
          });
          toast.present();
        },
        error: (err) => {
          console.error('Failed to save article', err);
          article.is_saved = false;
        }
      });
    } else {
      this.newsService.unsaveArticle(article.id, article.url).subscribe({
        next: async () => {
          const toast = await this.toastCtrl.create({
            message: 'Article removed from bookmarks',
            duration: 1500,
            position: 'bottom',
            color: 'dark'
          });
          toast.present();
        },
        error: (err) => {
          console.error('Failed to unsave article', err);
          article.is_saved = true;
        }
      });
    }
  }

  async shareArticle(article: NewsArticle, event: Event) {
    event.stopPropagation();
    if (navigator.share && article.url) {
      try {
        await navigator.share({
          title: article.title,
          text: article.summary,
          url: article.url
        });
      } catch (e) {
        // Share dismissed
      }
    } else {
      // Fallback copy link
      if (article.url && navigator.clipboard) {
        await navigator.clipboard.writeText(article.url);
        const toast = await this.toastCtrl.create({
          message: 'Link copied to clipboard!',
          duration: 2000,
          position: 'bottom',
          color: 'dark'
        });
        toast.present();
      }
    }
  }

  openUrl(url: string | undefined) {
    if (url) {
      window.open(url, '_blank', 'noopener,noreferrer');
    }
  }

  handleImageError(articleId: string) {
    this.imageErrors.add(articleId);
  }

  hasImageError(articleId: string): boolean {
    return this.imageErrors.has(articleId);
  }

  getCategoryBadgeClass(category?: string): string {
    const cat = (category || this.activeCategory || '').toLowerCase();
    if (cat.includes('tech')) return 'badge-tech';
    if (cat.includes('business')) return 'badge-biz';
    if (cat.includes('sport')) return 'badge-sports';
    if (cat.includes('health')) return 'badge-health';
    if (cat.includes('science')) return 'badge-science';
    if (cat.includes('world')) return 'badge-world';
    if (cat.includes('india')) return 'badge-india';
    return 'badge-general';
  }

  formatTimeAgo(dateStr?: string): string {
    if (!dateStr) return 'Recent';
    try {
      const date = new Date(dateStr);
      const now = new Date();
      const seconds = Math.floor((now.getTime() - date.getTime()) / 1000);
      
      if (seconds < 60) return 'Just now';
      const minutes = Math.floor(seconds / 60);
      if (minutes < 60) return `${minutes}m ago`;
      const hours = Math.floor(minutes / 60);
      if (hours < 24) return `${hours}h ago`;
      const days = Math.floor(hours / 24);
      if (days === 1) return 'Yesterday';
      if (days < 7) return `${days}d ago`;
      return date.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
    } catch {
      return 'Recent';
    }
  }

  cleanSummary(text: string): string {
    if (!text) return '';
    const cleaned = text.replace(/<[^>]*>/g, '').trim();
    return cleaned;
  }

  getArticleParagraphs(article: NewsArticle): string[] {
    if (article.full_coverage && Array.isArray(article.full_coverage) && article.full_coverage.length > 0) {
      return article.full_coverage;
    }
    const raw = article.content || article.summary || article.title;
    if (!raw) return [];
    
    // Split on double newlines or punctuation if single long text
    const paragraphs = raw.split(/\n\n+/).map(p => p.trim()).filter(p => p.length > 0);
    if (paragraphs.length <= 1 && raw.length > 200) {
      // Split on sentence clusters
      const sentences = raw.match(/[^.!?]+[.!?]+/g) || [raw];
      const chunks: string[] = [];
      let current = '';
      for (const s of sentences) {
        current += ' ' + s.trim();
        if (current.length > 220) {
          chunks.push(current.trim());
          current = '';
        }
      }
      if (current.trim()) chunks.push(current.trim());
      return chunks;
    }
    return paragraphs;
  }
}
