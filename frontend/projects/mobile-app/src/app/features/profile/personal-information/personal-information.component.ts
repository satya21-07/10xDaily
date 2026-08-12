import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule, Router } from '@angular/router';
import { IonicModule, ToastController, AlertController, LoadingController } from '@ionic/angular';
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
  arrowBack
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
      arrowBack
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
      const base64Image = e.target.result;
      
      const loading = await this.loadingCtrl.create({
        message: 'Updating profile picture...',
      });
      await loading.present();

      this.authService.updateAvatar(base64Image).subscribe({
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


