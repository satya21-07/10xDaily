import { Component } from '@angular/core';
import { IonicModule } from '@ionic/angular';
import { addIcons } from 'ionicons';
import { personOutline } from 'ionicons/icons';

@Component({
  selector: 'app-personal-information',
  standalone: true,
  imports: [IonicModule],
  templateUrl: './personal-information.component.html',
  styleUrl: './personal-information.component.scss'
})
export class PersonalInformationComponent {
  constructor() {
    addIcons({ personOutline });
  }
}
