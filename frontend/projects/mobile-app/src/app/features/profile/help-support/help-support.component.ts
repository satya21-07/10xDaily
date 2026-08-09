import { Component } from '@angular/core';
import { IonicModule } from '@ionic/angular';
import { addIcons } from 'ionicons';
import { helpCircleOutline } from 'ionicons/icons';

@Component({
  selector: 'app-help-support',
  standalone: true,
  imports: [IonicModule],
  templateUrl: './help-support.component.html',
  styleUrl: './help-support.component.scss'
})
export class HelpSupportComponent {
  constructor() {
    addIcons({ helpCircleOutline });
  }
}
