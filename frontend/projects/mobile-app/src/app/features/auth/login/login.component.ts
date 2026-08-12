import { Component, inject, NgZone, AfterViewInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { IonicModule, AlertController } from '@ionic/angular';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../../../services/auth.service';
import { environment } from '../../../../environments/environment';
import { addIcons } from 'ionicons';
import { personOutline, lockClosedOutline, rocket, logoGoogle, mailOutline, eyeOutline, eyeOffOutline, shieldCheckmarkOutline, logoApple } from 'ionicons/icons';

declare var google: any;

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, IonicModule, FormsModule],
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.scss']
})
export class LoginComponent implements AfterViewInit {
  private authService = inject(AuthService);
  private router = inject(Router);
  private ngZone = inject(NgZone);
  private alertCtrl = inject(AlertController);

  loginEmail = '';
  loginPassword = '';
  isLoggingIn = false;
  showPassword = false;

  constructor() {
    addIcons({ personOutline, lockClosedOutline, rocket, logoGoogle, mailOutline, eyeOutline, eyeOffOutline, shieldCheckmarkOutline, logoApple });
  }

  ngAfterViewInit() {
    this.initializeGoogleSignIn();
  }

  private initializeGoogleSignIn() {
    if (typeof window !== 'undefined' && typeof google !== 'undefined' && google.accounts) {
      google.accounts.id.initialize({
        client_id: environment.googleClientId,
        callback: this.handleCredentialResponse.bind(this)
      });
      google.accounts.id.renderButton(
        document.getElementById('google-btn-container'),
        { theme: 'outline', size: 'large', shape: 'rectangular', width: 280 }
      );
    } else {
      setTimeout(() => this.initializeGoogleSignIn(), 500);
    }
  }

  handleCredentialResponse(response: any) {
    this.isLoggingIn = true;
    this.authService.loginWithGoogle(response.credential).subscribe({
      next: () => {
        this.ngZone.run(() => {
          this.router.navigate(['/home']).then(() => {
            this.isLoggingIn = false;
          });
        });
      },
      error: async (err) => {
        console.error('Google login failed', err);
        this.isLoggingIn = false;
        
        const alert = await this.alertCtrl.create({
          header: 'Google Login Failed',
          message: err?.error?.detail || 'Please try again.',
          buttons: ['OK']
        });
        await alert.present();
      }
    });
  }

  onLogin() {
    if (!this.loginEmail || !this.loginPassword) return;
    
    this.isLoggingIn = true;
    
    this.authService.login(this.loginEmail, this.loginPassword).subscribe({
      next: () => {
        this.ngZone.run(() => {
          this.router.navigate(['/home']).then(() => {
            this.isLoggingIn = false;
          });
        });
      },
      error: async (err) => {
        console.error('Login failed', err);
        this.isLoggingIn = false;
        
        const alert = await this.alertCtrl.create({
          header: 'Login Failed',
          message: 'Please check your credentials and try again.',
          buttons: ['OK']
        });
        await alert.present();
      }
    });
  }

  goToRegister() {
    this.router.navigate(['/register']);
  }

  togglePassword() {
    this.showPassword = !this.showPassword;
  }

  goToForgotPassword() {
    console.log('Forgot password clicked');
    // Implement forgot password navigation here
  }
}
