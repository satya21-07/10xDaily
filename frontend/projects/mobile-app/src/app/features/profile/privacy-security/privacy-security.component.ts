import { Component } from '@angular/core';
import { IonicModule, ToastController } from '@ionic/angular';
import { addIcons } from 'ionicons';
import { RouterModule, Router } from '@angular/router';
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
  constructor(private toastCtrl: ToastController, private router: Router) {
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
    if (type === 'privacy') {
      this.router.navigate(['/privacy']);
      return;
    }
    
    if (type === 'terms') {
      this.router.navigate(['/terms']);
      return;
    }
    
    let url = 'https://10xdaily.online';
    if (type === 'support') {
      url = 'mailto:one0xdaily@gmail.com';
      window.location.href = url;
    }
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


