import { Component, OnInit, inject } from '@angular/core';
import { IonicModule } from '@ionic/angular';
import { addIcons } from 'ionicons';
import { notificationsOutline, flame, flameOutline, bookOutline, newspaperOutline, codeSlashOutline, fitnessOutline, medkitOutline, walletOutline, rocket, refreshOutline, chatboxEllipsesOutline, chevronForwardOutline, helpCircleOutline, playCircleOutline, arrowForwardOutline, personCircleOutline, sunnyOutline, moonOutline } from 'ionicons/icons';
import { RouterLink } from '@angular/router';
import { CommonModule } from '@angular/common';
import { QuoteService, DailyQuote } from '../../services/quote.service';
import { AuthService } from '../../services/auth.service';
import { OnThisDayService, OnThisDayEvent } from '../../services/on-this-day.service';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [IonicModule, RouterLink, CommonModule],
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.scss']
})
export class HomeComponent implements OnInit {
  private quoteService = inject(QuoteService);
  public authService = inject(AuthService);
  private onThisDayService = inject(OnThisDayService);
  
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
      personCircleOutline, sunnyOutline, moonOutline
    });
  }

  ngOnInit() {
    this.fetchNewQuote();
    this.fetchOnThisDayEvent();
  }
  
  fetchOnThisDayEvent() {
    this.isLoadingOnThisDay = true;
    this.onThisDayService.getTodayEvent().subscribe({
      next: (event) => {
        this.onThisDayEvent = event;
        this.isLoadingOnThisDay = false;
      },
      error: () => {
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
    if (hour < 12) return 'Good morning';
    if (hour < 18) return 'Good afternoon';
    return 'Good evening';
  }

  getGreetingIcon(): string {
    const hour = this.currentDate.getHours();
    if (hour < 18) return 'sunny-outline';
    return 'moon-outline';
  }
}
