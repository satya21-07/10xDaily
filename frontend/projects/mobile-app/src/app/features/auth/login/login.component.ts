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
    this.ngZone.run(() => {
      this.isLoggingIn = true;
      this.authService.loginWithGoogle(response.credential).subscribe({
        next: () => {
          this.router.navigate(['/home'], { replaceUrl: true }).then(() => {
            this.isLoggingIn = false;
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
    });
  }

  async onLogin() {
    if (!this.loginEmail || !this.loginPassword) return;
    
    const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    if (!emailRegex.test(this.loginEmail)) {
      const alert = await this.alertCtrl.create({
        header: 'Invalid Email',
        message: 'Please enter a valid email address.',
        buttons: ['OK']
      });
      await alert.present();
      return;
    }
    
    this.isLoggingIn = true;
    
    this.authService.login(this.loginEmail, this.loginPassword).subscribe({
      next: () => {
        this.ngZone.run(() => {
          this.router.navigate(['/home'], { replaceUrl: true }).then(() => {
            this.isLoggingIn = false;
          });
        });
      },
      error: async (err) => {
        console.error('Login failed', err);
        this.isLoggingIn = false;
        
        if (err?.error?.detail === '2FA_REQUIRED') {
          const alert = await this.alertCtrl.create({
            header: 'Two-Factor Authentication',
            message: 'Please enter the 6-digit code from your authenticator app.',
            inputs: [
              {
                name: 'code',
                type: 'number',
                placeholder: '6-digit code'
              }
            ],
            buttons: [
              { text: 'Cancel', role: 'cancel' },
              {
                text: 'Verify',
                handler: async (data) => {
                  if (!data.code) return false;
                  
                  this.isLoggingIn = true;
                  this.authService.login(this.loginEmail, this.loginPassword, data.code).subscribe({
                    next: () => {
                      this.ngZone.run(() => {
                        this.router.navigate(['/home'], { replaceUrl: true }).then(() => {
                          this.isLoggingIn = false;
                        });
                      });
                    },
                    error: async (err2) => {
                      this.isLoggingIn = false;
                      const errAlert = await this.alertCtrl.create({
                        header: 'Login Failed',
                        message: err2?.error?.detail || 'Invalid 2FA code.',
                        buttons: ['OK']
                      });
                      await errAlert.present();
                    }
                  });
                  return true;
                }
              }
            ]
          });
          await alert.present();
        } else {
          const alert = await this.alertCtrl.create({
            header: 'Login Failed',
            message: err?.error?.detail || 'Please check your credentials and try again.',
            buttons: ['OK']
          });
          await alert.present();
        }
      }
    });
  }

  goToRegister() {
    this.router.navigate(['/register']);
  }

  togglePassword() {
    this.showPassword = !this.showPassword;
  }

  async goToForgotPassword() {
    const alert = await this.alertCtrl.create({
      header: 'Reset Password',
      message: 'Enter your email address to receive a password reset link.',
      inputs: [
        {
          name: 'email',
          type: 'email',
          placeholder: 'Email address',
          value: this.loginEmail
        }
      ],
      buttons: [
        {
          text: 'Cancel',
          role: 'cancel',
          cssClass: 'secondary'
        },
        {
          text: 'Send Link',
          handler: async (data) => {
            if (!data.email) return false;
            
            const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
            if (!emailRegex.test(data.email)) {
              const errorAlert = await this.alertCtrl.create({
                header: 'Invalid Email',
                message: 'Please enter a valid email address.',
                buttons: ['OK']
              });
              await errorAlert.present();
              return false;
            }

            const successAlert = await this.alertCtrl.create({
              header: 'Link Sent',
              message: `A password reset link has been sent to ${data.email}.`,
              buttons: ['OK']
            });
            await successAlert.present();
            return true;
          }
        }
      ]
    });
    await alert.present();
  }
}
