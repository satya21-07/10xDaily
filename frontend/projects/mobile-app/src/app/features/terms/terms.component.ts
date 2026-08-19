import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { IonicModule } from '@ionic/angular';
import { RouterModule } from '@angular/router';
import { addIcons } from 'ionicons';
import { documentText, checkmarkCircle, warning, informationCircle } from 'ionicons/icons';

@Component({
  selector: 'app-terms',
  standalone: true,
  imports: [CommonModule, IonicModule, RouterModule],
  templateUrl: './terms.component.html',
  styleUrls: ['./terms.component.scss']
})
export class TermsComponent {
  currentDate = new Date();

  constructor() {
    addIcons({ documentText, checkmarkCircle, warning, informationCircle });
  }
}
