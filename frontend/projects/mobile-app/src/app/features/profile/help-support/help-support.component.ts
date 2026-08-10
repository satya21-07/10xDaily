import { Component } from '@angular/core';
import { IonicModule, AlertController } from '@ionic/angular';
import { RouterModule } from '@angular/router';
import { addIcons } from 'ionicons';
import { 
  helpCircleOutline, 
  bookOutline, 
  sparklesOutline, 
  bookmarkOutline, 
  newspaperOutline, 
  barChartOutline, 
  chevronForwardOutline, 
  searchOutline,
  arrowBack
} from 'ionicons/icons';

@Component({
  selector: 'app-help-support',
  standalone: true,
  imports: [IonicModule, RouterModule],
  templateUrl: './help-support.component.html',
  styleUrl: './help-support.component.scss'
})
export class HelpSupportComponent {

  helpArticles = {
    'How does 10xDaily work?': '10xDaily helps you learn new things every day through daily lessons, quizzes, and vocabulary. Just spend 10 minutes a day to level up your knowledge!',
    'How is my daily content generated?': 'Our content is curated using a mix of expert sources and advanced AI to ensure it is accurate, engaging, and easy to understand.',
    'How do I save an item?': 'You can save any lesson, word, or news article by tapping the bookmark icon. Find your saved items in the Bookmarks tab.',
    'How does News work?': 'We summarize the most important news from trusted sources globally, delivering concise updates so you stay informed quickly.',
    'How does Daily Quiz work?': 'Every day, you\'ll get a set of questions based on your recent lessons. Answer them to earn XP and track your learning progress.',
    'How is my progress calculated?': 'Your progress is calculated based on your daily streaks, quiz accuracy, and the number of lessons completed. Keep learning to level up!'
  };

  constructor(private alertController: AlertController) {
    addIcons({ 
      helpCircleOutline, 
      bookOutline, 
      sparklesOutline, 
      bookmarkOutline, 
      newspaperOutline, 
      barChartOutline, 
      chevronForwardOutline, 
      searchOutline,
      arrowBack
    });
  }

  async openArticle(title: string) {
    const content = this.helpArticles[title as keyof typeof this.helpArticles];
    if (content) {
      const alert = await this.alertController.create({
        header: title,
        message: content,
        buttons: ['Got it!']
      });
      await alert.present();
    }
  }
}
