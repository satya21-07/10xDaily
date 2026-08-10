import { Component } from '@angular/core';
import { IonicModule, ToastController } from '@ionic/angular';
import { addIcons } from 'ionicons';
import { RouterModule } from '@angular/router';
import { 
  shieldCheckmarkOutline, 
  shield, 
  lockClosed, 
  checkmarkCircle, 
  shieldOutline, 
  documentTextOutline, 
  optionsOutline, 
  chevronForwardOutline, 
  lockClosedOutline, 
  informationCircleOutline,
  arrowBack
} from 'ionicons/icons';

@Component({
  selector: 'app-privacy-security',
  standalone: true,
  imports: [IonicModule, RouterModule],
  templateUrl: './privacy-security.component.html',
  styleUrl: './privacy-security.component.scss'
})
export class PrivacySecurityComponent {
  constructor(private toastCtrl: ToastController) {
    addIcons({ 
      shieldCheckmarkOutline, 
      shield, 
      lockClosed, 
      checkmarkCircle, 
      shieldOutline, 
      documentTextOutline, 
      optionsOutline, 
      chevronForwardOutline, 
      lockClosedOutline, 
      informationCircleOutline,
      arrowBack
    });
  }

  openWebLink(type: string) {
    let url = 'https://10xdaily.app';
    if (type === 'privacy') {
      url += '/privacy';
    } else if (type === 'terms') {
      url += '/terms';
    } else if (type === 'support') {
      url = 'mailto:support@10xdaily.app';
    }
    window.open(url, '_blank');
  }

  async openDataPreferences() {
    const toast = await this.toastCtrl.create({
      message: 'Data Preferences will be available in the next update.',
      duration: 2000,
      position: 'bottom',
      color: 'dark'
    });
    toast.present();
  }

  async openSecurityTips() {
    const toast = await this.toastCtrl.create({
      message: 'Security Tips are coming soon!',
      duration: 2000,
      position: 'bottom',
      color: 'dark'
    });
    toast.present();
  }
}


