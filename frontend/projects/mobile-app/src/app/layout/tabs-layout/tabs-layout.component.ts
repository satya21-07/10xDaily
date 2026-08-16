import { Component } from '@angular/core';
import { IonicModule } from '@ionic/angular';
import { RouterModule } from '@angular/router';
import { addIcons } from 'ionicons';
import { home, helpCircle, bookmark, person, gameController } from 'ionicons/icons';
import { routeTransitionAnimations } from '../../shared/animations/route.animations';
import { ChildrenOutletContexts } from '@angular/router';

@Component({
  selector: 'app-tabs-layout',
  standalone: true,
  imports: [IonicModule, RouterModule],
  templateUrl: './tabs-layout.component.html',
  styleUrls: ['./tabs-layout.component.scss'],
  animations: [routeTransitionAnimations]
})
export class TabsLayoutComponent {
  constructor(private contexts: ChildrenOutletContexts) {
    addIcons({ home, helpCircle, bookmark, person, gameController });
  }

  getRouteAnimationData() {
    return this.contexts.getContext('primary')?.route?.snapshot?.url?.join('/') || 'default';
  }
}
