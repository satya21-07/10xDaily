import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { IonicModule } from '@ionic/angular';
import { RouterModule } from '@angular/router';
import { addIcons } from 'ionicons';
import { shieldCheckmark, lockClosed, eyeOff, documentText } from 'ionicons/icons';
import { RouterLink } from '@angular/router';
@Component({
  selector: 'app-privacy',
  standalone: true,
  imports: [CommonModule, IonicModule, RouterModule,RouterLink],
  templateUrl: './privacy.component.html',
  styleUrls: ['./privacy.component.scss']
})
export class PrivacyComponent {
  currentDate = new Date();

  constructor() {
    addIcons({ shieldCheckmark, lockClosed, eyeOff, documentText });
  }
}
