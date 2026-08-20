import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule, Router } from '@angular/router';
import { IonicModule, ToastController, AlertController, LoadingController, IonicSafeString } from '@ionic/angular';
import { addIcons } from 'ionicons';
import { 
  personOutline, 
  chevronForwardOutline, 
  pencilOutline, 
  lockClosedOutline, 
  shieldOutline, 
  trashOutline,
  saveOutline,
  closeOutline,
  arrowBack,
  copyOutline,
  checkmarkOutline
} from 'ionicons/icons';
import { AuthService, UserProfile } from '../../../services/auth.service';

@Component({
  selector: 'app-personal-information',
  standalone: true,
  imports: [IonicModule, CommonModule, FormsModule, RouterModule],
  templateUrl: './personal-information.component.html',
  styleUrl: './personal-information.component.scss'
})
export class PersonalInformationComponent implements OnInit {
  private authService = inject(AuthService);
  private toastCtrl = inject(ToastController);
  private alertCtrl = inject(AlertController);
  private loadingCtrl = inject(LoadingController);
  private router = inject(Router);
  
  user: UserProfile | null = null;
  twoFactorEnabled: boolean = false;
  
  isEditing = false;
  
  editName: string = '';
  editPhone: string = '';
  editDob: string = '';

  is2FAModalOpen = false;
  twoFactorQrCode = '';
  twoFactorSecret = '';
  twoFactorCodeInput = '';
  isSecretCopied = false;

  constructor() {
    addIcons({ 
      personOutline, 
      chevronForwardOutline, 
      pencilOutline, 
      lockClosedOutline, 
      shieldOutline, 
      trashOutline,
      saveOutline,
      closeOutline,
      arrowBack,
      copyOutline,
      checkmarkOutline
    });
  }

  ngOnInit() {
    this.authService.currentUser$.subscribe(profile => {
      this.user = profile;
    });
  }

  toggleEditMode() {
    if (!this.isEditing) {
      this.editName = this.user?.name || '';
      this.editPhone = this.user?.phoneNumber || '';
      this.editDob = this.user?.dateOfBirth || '';
    }
    this.isEditing = !this.isEditing;
  }
  
  cancelEdit() {
    this.isEditing = false;
  }

  async saveProfile() {
    if (this.editPhone) {
      const phoneRegex = /^\+?[0-9\s\-\(\)]{7,15}$/;
      if (!phoneRegex.test(this.editPhone)) {
        const alert = await this.alertCtrl.create({
          header: 'Invalid Phone Number',
          message: 'Please enter a valid phone number containing only numbers and standard formatting characters.',
          buttons: ['OK']
        });
        await alert.present();
        return;
      }
    }

    if (this.editDob) {
      const dateRegex = /^\d{4}-\d{2}-\d{2}$/;
      if (!dateRegex.test(this.editDob)) {
        const alert = await this.alertCtrl.create({
          header: 'Invalid Date',
          message: 'Please enter a valid date of birth (YYYY-MM-DD).',
          buttons: ['OK']
        });
        await alert.present();
        return;
      }
      
      const dobDate = new Date(this.editDob);
      if (dobDate > new Date()) {
         const alert = await this.alertCtrl.create({
          header: 'Invalid Date',
          message: 'Date of birth cannot be in the future.',
          buttons: ['OK']
        });
        await alert.present();
        return;
      }
    }

    const loading = await this.loadingCtrl.create({
      message: 'Saving...',
    });
    await loading.present();

    const data = {
      full_name: this.editName,
      phone_number: this.editPhone,
      date_of_birth: this.editDob
    };

    this.authService.updateProfile(data).subscribe({
      next: async () => {
        await loading.dismiss();
        this.isEditing = false;
        const toast = await this.toastCtrl.create({
          message: 'Profile updated successfully',
          duration: 2000,
          color: 'success',
          position: 'bottom'
        });
        toast.present();
      },
      error: async (err) => {
        await loading.dismiss();
        const toast = await this.toastCtrl.create({
          message: 'Failed to update profile. Please try again.',
          duration: 3000,
          color: 'danger',
          position: 'bottom'
        });
        toast.present();
      }
    });
  }

  async showComingSoon(featureName: string) {
    if (this.isEditing) return; // Disable standard clicks during edit mode
    
    const toast = await this.toastCtrl.create({
      message: `${featureName} will be available soon.`,
      duration: 2000,
      position: 'bottom',
      color: 'dark'
    });
    toast.present();
  }

  async manage2FA() {
    if (this.isEditing) return;
    
    if (this.user?.isTwoFactorEnabled) {
      const alert = await this.alertCtrl.create({
        header: 'Disable 2FA',
        message: 'Are you sure you want to disable Two-Factor Authentication? Your account will be less secure.',
        buttons: [
          { text: 'Cancel', role: 'cancel' },
          { 
            text: 'Disable', 
            role: 'destructive',
            handler: async () => {
              const loading = await this.loadingCtrl.create({ message: 'Disabling...' });
              await loading.present();
              this.authService.disable2FA().subscribe({
                next: async () => {
                  await loading.dismiss();
                  const toast = await this.toastCtrl.create({
                    message: 'Two-Factor Authentication disabled.',
                    duration: 2000,
                    color: 'success',
                    position: 'bottom'
                  });
                  toast.present();
                },
                error: async () => {
                  await loading.dismiss();
                  const toast = await this.toastCtrl.create({
                    message: 'Failed to disable 2FA.',
                    duration: 2000,
                    color: 'danger',
                    position: 'bottom'
                  });
                  toast.present();
                }
              });
            }
          }
        ]
      });
      await alert.present();
    } else {
      const loading = await this.loadingCtrl.create({ message: 'Initializing 2FA...' });
      await loading.present();
      
      this.authService.setup2FA().subscribe({
        next: async (res) => {
          await loading.dismiss();
          this.twoFactorSecret = res.secret;
          this.twoFactorQrCode = res.qr_code;
          this.twoFactorCodeInput = '';
          this.isSecretCopied = false;
          this.is2FAModalOpen = true;
        },
        error: async () => {
          await loading.dismiss();
          const toast = await this.toastCtrl.create({
            message: 'Failed to initialize 2FA setup.',
            duration: 2000,
            color: 'danger',
            position: 'bottom'
          });
          toast.present();
        }
      });
    }
  }

  close2FAModal() {
    this.is2FAModalOpen = false;
    this.twoFactorCodeInput = '';
    this.isSecretCopied = false;
  }

  async copySecret() {
    if (navigator.clipboard && this.twoFactorSecret) {
      try {
        await navigator.clipboard.writeText(this.twoFactorSecret);
        this.isSecretCopied = true;
        setTimeout(() => {
          this.isSecretCopied = false;
        }, 2000);
      } catch (err) {
        console.error('Failed to copy', err);
      }
    }
  }

  async verify2FACode() {
    if (!this.twoFactorCodeInput || this.twoFactorCodeInput.toString().length !== 6) {
      const toast = await this.toastCtrl.create({
        message: 'Please enter a valid 6-digit code.',
        duration: 2000,
        color: 'danger',
        position: 'bottom'
      });
      toast.present();
      return;
    }
    
    const verifyLoading = await this.loadingCtrl.create({ message: 'Verifying...' });
    await verifyLoading.present();
    
    this.authService.verify2FA(this.twoFactorCodeInput.toString(), this.twoFactorSecret).subscribe({
      next: async () => {
        await verifyLoading.dismiss();
        this.close2FAModal();
        const toast = await this.toastCtrl.create({
          message: 'Two-Factor Authentication enabled successfully!',
          duration: 2000,
          color: 'success',
          position: 'bottom'
        });
        toast.present();
      },
      error: async (err) => {
        await verifyLoading.dismiss();
        const errToast = await this.toastCtrl.create({
          message: err.error?.detail || 'Invalid code. Please try again.',
          duration: 2000,
          color: 'danger',
          position: 'bottom'
        });
        errToast.present();
      }
    });
  }

  async changePassword() {
    if (this.isEditing) return; // Disable standard clicks during edit mode

    const alert = await this.alertCtrl.create({
      header: 'Change Password',
      inputs: [
        {
          name: 'currentPassword',
          type: 'password',
          placeholder: 'Current Password'
        },
        {
          name: 'newPassword',
          type: 'password',
          placeholder: 'New Password'
        },
        {
          name: 'confirmPassword',
          type: 'password',
          placeholder: 'Confirm New Password'
        }
      ],
      buttons: [
        {
          text: 'Cancel',
          role: 'cancel',
          cssClass: 'secondary'
        },
        {
          text: 'Update',
          handler: async (data) => {
            if (!data.currentPassword || !data.newPassword || !data.confirmPassword) {
              const err = await this.alertCtrl.create({
                header: 'Error',
                message: 'All fields are required.',
                buttons: ['OK']
              });
              await err.present();
              return false;
            }
            
            if (data.newPassword !== data.confirmPassword) {
              const err = await this.alertCtrl.create({
                header: 'Error',
                message: 'New passwords do not match.',
                buttons: ['OK']
              });
              await err.present();
              return false;
            }
            
            const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&#])[A-Za-z\d@$!%*?&#]{8,}$/;
            if (!passwordRegex.test(data.newPassword)) {
              const err = await this.alertCtrl.create({
                header: 'Weak Password',
                message: 'Password must be at least 8 characters long and contain at least one uppercase letter, one lowercase letter, one number, and one special character.',
                buttons: ['OK']
              });
              await err.present();
              return false;
            }

            const loading = await this.loadingCtrl.create({
              message: 'Updating password...',
            });
            await loading.present();

            this.authService.changePassword(data.currentPassword, data.newPassword).subscribe({
              next: async () => {
                await loading.dismiss();
                const success = await this.alertCtrl.create({
                  header: 'Success',
                  message: 'Your password has been updated successfully.',
                  buttons: ['OK']
                });
                await success.present();
              },
              error: async (err) => {
                await loading.dismiss();
                const errAlert = await this.alertCtrl.create({
                  header: 'Update Failed',
                  message: err?.error?.detail || 'Failed to update password. Please check your current password.',
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
  }

  triggerFileInput() {
    if (!this.isEditing) {
      this.showComingSoon('Profile Picture Update (Click Edit first)');
      return;
    }
    const fileInput = document.getElementById('avatar-input') as HTMLInputElement;
    if (fileInput) {
      fileInput.click();
    }
  }

  async onFileSelected(event: any) {
    const file = event.target.files[0];
    if (!file) return;

    if (!file.type.startsWith('image/')) {
      const toast = await this.toastCtrl.create({
        message: 'Please select a valid image file.',
        duration: 2000,
        position: 'bottom',
        color: 'danger'
      });
      toast.present();
      return;
    }

    const reader = new FileReader();
    reader.onload = async (e: any) => {
      const img = new Image();
      img.onload = async () => {
        const canvas = document.createElement('canvas');
        const MAX_WIDTH = 512;
        const MAX_HEIGHT = 512;
        let width = img.width;
        let height = img.height;

        if (width > height) {
          if (width > MAX_WIDTH) {
            height = Math.round(height *= MAX_WIDTH / width);
            width = MAX_WIDTH;
          }
        } else {
          if (height > MAX_HEIGHT) {
            width = Math.round(width *= MAX_HEIGHT / height);
            height = MAX_HEIGHT;
          }
        }

        canvas.width = width;
        canvas.height = height;
        const ctx = canvas.getContext('2d');
        if (ctx) {
          ctx.drawImage(img, 0, 0, width, height);
          const compressedBase64 = canvas.toDataURL('image/webp', 0.8);
          
          const loading = await this.loadingCtrl.create({
            message: 'Updating profile picture...',
          });
          await loading.present();

          this.authService.updateAvatar(compressedBase64).subscribe({
            next: async () => {
              await loading.dismiss();
              const toast = await this.toastCtrl.create({
                message: 'Profile picture updated successfully!',
                duration: 2000,
                color: 'success',
                position: 'bottom'
              });
              toast.present();
            },
            error: async (err) => {
              await loading.dismiss();
              const toast = await this.toastCtrl.create({
                message: 'Failed to update profile picture. Please try again.',
                duration: 3000,
                color: 'danger',
                position: 'bottom'
              });
              toast.present();
            }
          });
        }
      };
      img.src = e.target.result;
    };
    reader.readAsDataURL(file);
  }

  async confirmDelete() {
    const alert = await this.alertCtrl.create({
      header: 'Delete Account',
      message: 'Are you sure you want to permanently delete your account? This action cannot be undone.',
      buttons: [
        {
          text: 'Cancel',
          role: 'cancel',
          cssClass: 'secondary'
        }, {
          text: 'Delete',
          cssClass: 'danger',
          handler: async () => {
            const loading = await this.loadingCtrl.create({
              message: 'Deleting account...',
            });
            await loading.present();

            this.authService.deleteAccount().subscribe({
              next: async () => {
                await loading.dismiss();
                const toast = await this.toastCtrl.create({
                  message: 'Account deleted successfully',
                  duration: 2000,
                  color: 'success',
                  position: 'bottom'
                });
                toast.present();
                this.router.navigate(['/welcome']);
              },
              error: async (err) => {
                await loading.dismiss();
                const toast = await this.toastCtrl.create({
                  message: 'Failed to delete account. Please try again.',
                  duration: 3000,
                  color: 'danger',
                  position: 'bottom'
                });
                toast.present();
              }
            });
          }
        }
      ]
    });
    await alert.present();
  }
}


