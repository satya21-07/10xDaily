import { Component, inject, NgZone } from '@angular/core';
import { CommonModule } from '@angular/common';
import { IonicModule, AlertController } from '@ionic/angular';
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
  private alertCtrl = inject(AlertController);

  registerName = '';
  registerEmail = '';
  registerPassword = '';
  isRegistering = false;

  constructor() {
    addIcons({ personOutline, lockClosedOutline, rocket, mailOutline });
  }

  async onRegister() {
    if (!this.registerEmail || !this.registerPassword || !this.registerName) return;
    
    // Password validation: min 8 chars, 1 uppercase, 1 lowercase, 1 number, 1 special character
    const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&#])[A-Za-z\d@$!%*?&#]{8,}$/;
    if (!passwordRegex.test(this.registerPassword)) {
      const alert = await this.alertCtrl.create({
        header: 'Weak Password',
        message: 'Password must be at least 8 characters long and contain at least one uppercase letter, one lowercase letter, one number, and one special character.',
        buttons: ['OK']
      });
      await alert.present();
      return;
    }
    
    this.isRegistering = true;
    
    this.authService.register(this.registerEmail, this.registerPassword, this.registerName).subscribe({
      next: () => {
        this.isRegistering = false;
        this.ngZone.run(() => {
          this.router.navigate(['/home']);
        });
      },
      error: async (err) => {
        console.error('Registration failed', err);
        this.isRegistering = false;
        
        const alert = await this.alertCtrl.create({
          header: 'Registration Failed',
          message: err?.error?.detail || 'Please check your inputs.',
          buttons: ['OK']
        });
        await alert.present();
      }
    });
  }

  goToLogin() {
    this.router.navigate(['/login']);
  }
}
