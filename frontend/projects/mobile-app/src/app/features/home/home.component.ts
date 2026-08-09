import { Component, OnInit, inject } from '@angular/core';
import { IonicModule } from '@ionic/angular';
import { addIcons } from 'ionicons';
import { notificationsOutline, flame, bookOutline, newspaperOutline, codeSlashOutline, fitnessOutline, medkitOutline, walletOutline, rocket, refreshOutline, chatboxEllipsesOutline, chevronForwardOutline, helpCircleOutline, playCircleOutline } from 'ionicons/icons';
import { RouterLink } from '@angular/router';
import { CommonModule } from '@angular/common';
import { QuoteService, DailyQuote } from '../../services/quote.service';
import { AuthService } from '../../services/auth.service';

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
  
  currentDate = new Date();
  quoteOfTheDay: DailyQuote = { text: 'Loading...', author: '' };
  isLoadingQuote = true;

  constructor() {
    addIcons({ 
      notificationsOutline, flame, bookOutline, 
      newspaperOutline, codeSlashOutline, fitnessOutline, 
      medkitOutline, walletOutline, rocket, refreshOutline,
      chatboxEllipsesOutline, chevronForwardOutline, helpCircleOutline, playCircleOutline
    });
  }

  ngOnInit() {
    this.fetchNewQuote();
  }
  
  fetchNewQuote(event?: any) {
    this.isLoadingQuote = true;
    this.quoteService.getRandomQuote().subscribe({
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
