import { Component, OnInit, inject } from '@angular/core';
import { IonicModule } from '@ionic/angular';
import { addIcons } from 'ionicons';
import { notificationsOutline, flame, bookOutline, newspaperOutline, codeSlashOutline, fitnessOutline, medkitOutline, walletOutline, rocket, refreshOutline, chatboxEllipsesOutline, chevronForwardOutline, helpCircleOutline, playCircleOutline, arrowForwardOutline, personCircleOutline } from 'ionicons/icons';
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
      notificationsOutline, flame, bookOutline, 
      newspaperOutline, codeSlashOutline, fitnessOutline, 
      medkitOutline, walletOutline, rocket, refreshOutline,
      chatboxEllipsesOutline, chevronForwardOutline, helpCircleOutline, playCircleOutline, arrowForwardOutline,
      personCircleOutline
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
}
