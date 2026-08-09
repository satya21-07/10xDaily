import { Component, OnInit } from '@angular/core';
import { IonicModule, ActionSheetController } from '@ionic/angular';
import { CommonModule } from '@angular/common';
import { BookmarkService, Bookmark } from '../../core/services/bookmark.service';
import { NewsService } from '../../services/news.service';
import { addIcons } from 'ionicons';
import { bookOutline, newspaperOutline, codeSlashOutline, medkitOutline, leafOutline, cashOutline, bookmarkOutline, searchOutline, optionsOutline, volumeHighOutline, bookmark, ellipsisVertical, trashOutline, chevronForwardOutline } from 'ionicons/icons';

@Component({
  selector: 'app-bookmarks',
  standalone: true,
  imports: [IonicModule, CommonModule],
  templateUrl: './bookmarks.component.html',
  styleUrl: './bookmarks.component.scss'
})
export class BookmarksComponent implements OnInit {
  bookmarks: Bookmark[] = [];
  groupedBookmarks: { [key: string]: Bookmark[] } = {};
  topics: string[] = [];
  activeSegment: string = '';

  tabConfig: { [key: string]: { label: string, icon: string, suffix: string } } = {
    'vocabulary': { label: 'Vocabulary', icon: 'book-outline', suffix: 'words' },
    'news': { label: 'Articles', icon: 'newspaper-outline', suffix: 'articles' },
    'coding': { label: 'Coding', icon: 'code-slash-outline', suffix: 'items' },
    'health': { label: 'Health', icon: 'medkit-outline', suffix: 'items' },
    'spiritual': { label: 'Spiritual', icon: 'leaf-outline', suffix: 'items' },
    'finance': { label: 'Finance', icon: 'cash-outline', suffix: 'items' },
    'Other': { label: 'Other', icon: 'bookmark-outline', suffix: 'items' }
  };

  constructor(
    private bookmarkService: BookmarkService,
    private newsService: NewsService,
    private actionSheetCtrl: ActionSheetController
  ) {
    addIcons({ bookOutline, newspaperOutline, codeSlashOutline, medkitOutline, leafOutline, cashOutline, bookmarkOutline, searchOutline, optionsOutline, volumeHighOutline, bookmark, ellipsisVertical, trashOutline, chevronForwardOutline });
  }

  ngOnInit() {
    this.loadBookmarks();
  }

  ionViewWillEnter() {
    this.loadBookmarks();
  }

  loadBookmarks() {
    // We now have two sources: BookmarkService for general bookmarks, NewsService for SavedNews
    let generalBookmarks: Bookmark[] = [];
    let savedNewsBookmarks: any[] = [];
    
    let completedRequests = 0;
    const checkCompletion = () => {
      completedRequests++;
      if (completedRequests === 2) {
        this.bookmarks = [...generalBookmarks, ...savedNewsBookmarks];
        this.groupBookmarks();
      }
    };

    this.bookmarkService.getBookmarks().subscribe({
      next: (data) => {
        generalBookmarks = data;
        checkCompletion();
      },
      error: (err) => {
        console.error('Error fetching bookmarks:', err);
        checkCompletion();
      }
    });

    this.newsService.getSavedNews().subscribe({
      next: (data) => {
        // Transform SavedNewsResponse into Bookmark-like format for grouping
        savedNewsBookmarks = data.map(news => ({
          id: news.id,
          title: news.title,
          url: news.url,
          content_type: 'news',
          created_at: news.saved_at,
          parsed_data: news, // Pass the whole object as parsed_data
          is_saved_news_record: true,
          article_id: news.article_id
        }));
        checkCompletion();
      },
      error: (err) => {
        console.error('Error fetching saved news:', err);
        checkCompletion();
      }
    });
  }

  groupBookmarks() {
    this.groupedBookmarks = {};
    this.bookmarks.forEach((b: any) => {
      const type = b.content_type || 'Other';
      if (!this.groupedBookmarks[type]) {
        this.groupedBookmarks[type] = [];
      }
      if (!b.is_saved_news_record) {
        try {
          b.parsed_data = b.details ? JSON.parse(b.details) : null;
        } catch (e) {
          b.parsed_data = null;
        }
      }
      this.groupedBookmarks[type].push(b);
    });
    this.topics = Object.keys(this.groupedBookmarks);
    
    if (this.topics.length > 0 && !this.topics.includes(this.activeSegment)) {
      this.activeSegment = this.topics.includes('vocabulary') ? 'vocabulary' : this.topics[0];
    }
  }

  getTabLabel(type: string): string {
    return this.tabConfig[type]?.label || type;
  }

  getTabIcon(type: string): string {
    return this.tabConfig[type]?.icon || 'bookmark-outline';
  }

  getSavedText(topic: string, count: number): string {
    const suffix = this.tabConfig[topic]?.suffix || 'items';
    return `${count} saved ${suffix}`;
  }

  getSynonyms(item: any): string {
    if (!item?.parsed_data) return '';
    
    let synonyms: string[] = [];
    if (Array.isArray(item.parsed_data.synonyms)) {
      synonyms = item.parsed_data.synonyms;
    } else if (typeof item.parsed_data.synonyms === 'string') {
      return item.parsed_data.synonyms;
    } else if (item.parsed_data.definitions?.[0]?.synonyms) {
      synonyms = item.parsed_data.definitions[0].synonyms;
    }
    
    return Array.isArray(synonyms) ? synonyms.slice(0, 4).join(', ') : '';
  }

  async presentOptions(item: any, event: Event) {
    event.stopPropagation();
    if (!item || !item.id) return;
    
    const actionSheet = await this.actionSheetCtrl.create({
      header: 'Options',
      cssClass: 'compact-action-sheet',
      buttons: [
        {
          text: 'Remove from Saved Items',
          role: 'destructive',
          icon: 'trash-outline',
          handler: () => {
            this.deleteBookmark(item);
          }
        },
        {
          text: 'Cancel',
          role: 'cancel'
        }
      ]
    });
    await actionSheet.present();
  }

  deleteBookmark(item: any) {
    if (item.is_saved_news_record) {
      this.newsService.unsaveArticle(item.article_id, item.url).subscribe({
        next: () => this.loadBookmarks(),
        error: (err) => console.error('Error removing saved news:', err)
      });
    } else {
      this.bookmarkService.deleteBookmark(item.id).subscribe(() => {
        this.loadBookmarks();
      });
    }
  }

  formatDate(dateString?: string): string {
    if (!dateString) return '';
    const date = new Date(dateString);
    const options: Intl.DateTimeFormatOptions = { day: 'numeric', month: 'short', year: 'numeric' };
    return date.toLocaleDateString('en-GB', options);
  }
  
  playAudio(url: string | undefined, word: string, event: Event) {
    event.stopPropagation();
    if (url) {
       const audio = new Audio(url);
       audio.play().catch(e => {
         console.error("Error playing audio url, falling back to TTS:", e);
         this.speakWord(word);
       });
    } else {
       this.speakWord(word);
    }
  }

  private speakWord(text: string) {
    if ('speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = 'en-US';
      utterance.rate = 0.85; 
      window.speechSynthesis.speak(utterance);
    } else {
      console.warn("Text-to-speech not supported in this browser.");
    }
  }
}
