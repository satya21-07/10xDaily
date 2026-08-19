import { Component, OnInit, OnDestroy, inject } from '@angular/core';
import { IonicModule } from '@ionic/angular';
import { addIcons } from 'ionicons';
import { notificationsOutline, flame, flameOutline, bookOutline, newspaperOutline, codeSlashOutline, fitnessOutline, medkitOutline, walletOutline, rocket, refreshOutline, chatboxEllipsesOutline, chevronForwardOutline, helpCircleOutline, playCircleOutline, arrowForwardOutline, personCircleOutline, sunnyOutline, moonOutline, gameControllerOutline, checkmarkCircle, calendarOutline, compassOutline, play } from 'ionicons/icons';
import { RouterLink } from '@angular/router';
import { CommonModule } from '@angular/common';
import { QuoteService, DailyQuote } from '../../services/quote.service';
import { AuthService } from '../../services/auth.service';
import { OnThisDayService, OnThisDayEvent } from '../../services/on-this-day.service';
import { ProgressService } from '../../services/progress.service';
import { Subscription } from 'rxjs';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [IonicModule, RouterLink, CommonModule],
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.scss']
})
export class HomeComponent implements OnInit, OnDestroy {
  private quoteService = inject(QuoteService);
  public authService = inject(AuthService);
  private onThisDayService = inject(OnThisDayService);
  private progressService = inject(ProgressService);
  private progressSub?: Subscription;
  
  currentDate = new Date();
  quoteOfTheDay: DailyQuote = { text: 'Loading...', author: '' };
  isLoadingQuote = true;

  onThisDayEvent: OnThisDayEvent | null = null;
  isLoadingOnThisDay = true;

  constructor() {
    addIcons({ 
      notificationsOutline, flame, flameOutline, bookOutline, 
      newspaperOutline, codeSlashOutline, fitnessOutline, 
      medkitOutline, walletOutline, rocket, refreshOutline,
      chatboxEllipsesOutline, chevronForwardOutline, helpCircleOutline, playCircleOutline, arrowForwardOutline,
      personCircleOutline, sunnyOutline, moonOutline, gameControllerOutline, checkmarkCircle,
      calendarOutline, compassOutline, play
    });
  }

  ngOnInit() {
    this.fetchNewQuote();
    this.fetchOnThisDayEvent();
    
    this.progressSub = this.progressService.visitedModules$.subscribe(visited => {
      const items = this.topics.map(t => ({
        id: t.id,
        label: t.shortLabel,
        icon: visited.has(t.id) ? 'checkmark-circle' : t.icon,
        status: visited.has(t.id) ? 'completed' : 'pending'
      }));
      this.progress = {
        completed: items.filter(i => i.status === 'completed').length,
        total: items.length,
        items
      };
    });
  }
  
  ngOnDestroy() {
    if (this.progressSub) {
      this.progressSub.unsubscribe();
    }
  }
  
  fetchOnThisDayEvent() {
    this.isLoadingOnThisDay = true;
    this.onThisDayService.getTodayEvent().subscribe({
      next: (event) => {
        this.onThisDayEvent = event;
        this.isLoadingOnThisDay = false;
      },
      error: (err) => {
        console.error('Error fetching OnThisDay:', err);
        this.isLoadingOnThisDay = false;
      }
    });
  }

  fetchNewQuote(event?: any) {
    this.isLoadingQuote = true;
    this.quoteService.getDailyQuote().subscribe({
      next: (quote) => {
        this.quoteOfTheDay = quote;
        this.isLoadingQuote = false;
        if (event) {
          event.target.complete();
        }
      },
      error: () => {
        this.isLoadingQuote = false;
        if (event) {
          event.target.complete();
        }
      }
    });
  }

  getFirstName(name?: string): string {
    if (!name) return 'Explorer';
    return name.split(' ')[0];
  }

  getInitials(name?: string): string {
    if (!name) return 'EX';
    const parts = name.trim().split(' ');
    if (parts.length >= 2) {
      return (parts[0][0] + parts[1][0]).toUpperCase();
    }
    return name.substring(0, 2).toUpperCase();
  }

  getGreeting(): string {
    const hour = this.currentDate.getHours();
    if (hour >= 5 && hour < 12) return 'Good morning';
    if (hour >= 12 && hour < 17) return 'Good afternoon';
    if (hour >= 17 && hour < 21) return 'Good evening';
    return 'Good night';
  }

  getGreetingIcon(): string {
    const hour = this.currentDate.getHours();
    if (hour >= 5 && hour < 18) return 'sunny-outline';
    return 'moon-outline';
  }

  getBackgroundImage(): string {
    const hour = this.currentDate.getHours();
    if (hour >= 5 && hour < 12) return "url('assets/morning-bg.jpg')";
    if (hour >= 12 && hour < 17) return "url('assets/afternoon-bg.jpg')";
    if (hour >= 17 && hour < 21) return "url('assets/evening-bg.jpg')";
    return "url('assets/night-bg.jpg')";
  }

  getTimeClass(): string {
    const hour = this.currentDate.getHours();
    if (hour >= 5 && hour < 12) return 'time-morning';
    if (hour >= 12 && hour < 17) return 'time-afternoon';
    if (hour >= 17 && hour < 21) return 'time-evening';
    return 'time-night';
  }

  progress = {
    completed: 0,
    total: 6,
    items: [] as any[]
  };

  topics = [
    { id: 'vocabulary', title: 'Vocabulary', desc: '10 new words', route: '/vocabulary', icon: 'book-outline', cssClass: 'blue-card', shortLabel: 'Vocab' },
    { id: 'news', title: 'Daily news', desc: 'India and world', route: '/news', icon: 'newspaper-outline', cssClass: 'peach-card', shortLabel: 'News' },
    { id: 'coding', title: 'Coding', desc: 'DSA mastery', route: '/coding', icon: 'code-slash-outline', cssClass: 'purple-card', shortLabel: 'Coding' },
    { id: 'spiritual', title: 'Spiritual', desc: 'Mythology tales', route: '/spiritual', icon: 'moon-outline', cssClass: 'blue-card', shortLabel: 'Spirit' },
    { id: 'finance', title: 'Finance', desc: 'Market updates', route: '/finance', icon: 'wallet-outline', cssClass: 'peach-card', shortLabel: 'Finance' },
    { id: 'health', title: 'Health', desc: 'Fitness tips', route: '/health', icon: 'fitness-outline', cssClass: 'purple-card', shortLabel: 'Health' }
  ];

  getProgressWidth(): string {
    if (this.progress.total <= 1) return '0%';
    if (this.progress.completed <= 1) return '0%';
    const pct = ((this.progress.completed - 1) / (this.progress.total - 1)) * 100;
    return `${pct}%`;
  }
}
