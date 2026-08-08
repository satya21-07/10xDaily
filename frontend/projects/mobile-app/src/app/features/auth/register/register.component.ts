import { Component, inject, NgZone } from '@angular/core';
import { CommonModule } from '@angular/common';
import { IonicModule } from '@ionic/angular';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../../../services/auth.service';
import { addIcons } from 'ionicons';
import { personOutline, lockClosedOutline, rocket, mailOutline } from 'ionicons/icons';

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [CommonModule, IonicModule, FormsModule],
  templateUrl: './register.component.html',
  styleUrls: ['./register.component.scss']
})
export class RegisterComponent {
  private authService = inject(AuthService);
  private router = inject(Router);
  private ngZone = inject(NgZone);

  registerName = '';
  registerEmail = '';
  registerPassword = '';
  isRegistering = false;

  constructor() {
    addIcons({ personOutline, lockClosedOutline, rocket, mailOutline });
  }

  onRegister() {
    if (!this.registerEmail || !this.registerPassword || !this.registerName) return;
    
    this.isRegistering = true;
    
    this.authService.register(this.registerEmail, this.registerPassword, this.registerName).subscribe({
      next: () => {
        this.isRegistering = false;
        this.ngZone.run(() => {
          this.router.navigate(['/home']);
        });
      },
      error: (err) => {
        console.error('Registration failed', err);
        this.isRegistering = false;
        alert('Registration failed. ' + (err?.error?.detail || 'Please check your inputs.'));
      }
    });
  }

  goToLogin() {
    this.router.navigate(['/login']);
  }
}
