import { Component } from '@angular/core';
import { IonicModule } from '@ionic/angular';
import { RouterModule } from '@angular/router';
import { addIcons } from 'ionicons';
import { home, helpCircle, bookmark, person } from 'ionicons/icons';

@Component({
  selector: 'app-tabs-layout',
  standalone: true,
  imports: [IonicModule, RouterModule],
  templateUrl: './tabs-layout.component.html',
  styleUrls: ['./tabs-layout.component.scss']
})
export class TabsLayoutComponent {
  constructor() {
    addIcons({ home, helpCircle, bookmark, person });
  }
}
