import { Component } from '@angular/core';
import { IonicModule } from '@ionic/angular';
import { addIcons } from 'ionicons';
import { shieldCheckmarkOutline } from 'ionicons/icons';

@Component({
  selector: 'app-privacy-security',
  standalone: true,
  imports: [IonicModule],
  templateUrl: './privacy-security.component.html',
  styleUrl: './privacy-security.component.scss'
})
export class PrivacySecurityComponent {
  constructor() {
    addIcons({ shieldCheckmarkOutline });
  }
}
