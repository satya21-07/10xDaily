import { Component, inject, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterOutlet, RouterLink, RouterLinkActive, Router } from '@angular/router';
import { MatSidenavModule } from '@angular/material/sidenav';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatListModule } from '@angular/material/list';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatMenuModule } from '@angular/material/menu';
import { BreakpointObserver, Breakpoints } from '@angular/cdk/layout';
import { Subject, takeUntil } from 'rxjs';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-dashboard-layout',
  standalone: true,
  imports: [
    CommonModule, 
    RouterOutlet, 
    RouterLink, 
    RouterLinkActive,
    MatSidenavModule,
    MatToolbarModule,
    MatListModule,
    MatIconModule,
    MatButtonModule,
    MatMenuModule
  ],
  templateUrl: './dashboard-layout.component.html',
  styleUrls: ['./dashboard-layout.component.scss']
})
export class DashboardLayoutComponent implements OnInit, OnDestroy {
  private authService = inject(AuthService);
  private router = inject(Router);
  private breakpointObserver = inject(BreakpointObserver);
  private destroy$ = new Subject<void>();

  isMobile = false;

  menuItems = [
    { path: '/dashboard', icon: 'dashboard', label: 'Dashboard' },
    { path: '/content', icon: 'article', label: 'Content Manager' },
    { path: '/users', icon: 'people', label: 'Users' },
    { path: '/analytics', icon: 'analytics', label: 'Analytics (Coming Soon)' }
  ];

  ngOnInit() {
    this.breakpointObserver
      .observe([Breakpoints.XSmall, Breakpoints.Small])
      .pipe(takeUntil(this.destroy$))
      .subscribe(result => {
        this.isMobile = result.matches;
      });
  }

  ngOnDestroy() {
    this.destroy$.next();
    this.destroy$.complete();
  }

  logout() {
    this.authService.logout();
    this.router.navigate(['/login']);
  }
}
