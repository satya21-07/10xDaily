import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule, Router } from '@angular/router';
import { IonicModule, ToastController, LoadingController } from '@ionic/angular';
import { addIcons } from 'ionicons';
import { 
  arrowBack, 
  paperPlaneOutline, 
  star, 
  starOutline, 
  checkmarkCircle, 
  bugOutline, 
  bulbOutline, 
  chatbubbleEllipsesOutline, 
  bookOutline, 
  informationCircleOutline,
  alertCircleOutline,
  sparklesOutline
} from 'ionicons/icons';
import { AuthService, UserProfile } from '../../../services/auth.service';
import { FeedbackService } from '../../../services/feedback.service';
import { FeedbackType } from '../../../models/feedback.model';

@Component({
  selector: 'app-feedback',
  standalone: true,
  imports: [IonicModule, CommonModule, FormsModule, RouterModule],
  templateUrl: './feedback.component.html',
  styleUrl: './feedback.component.scss'
})
export class FeedbackComponent implements OnInit {
  private authService = inject(AuthService);
  private feedbackService = inject(FeedbackService);
  private toastCtrl = inject(ToastController);
  private loadingCtrl = inject(LoadingController);
  private router = inject(Router);

  user: UserProfile | null = null;

  // Form fields
  selectedType: FeedbackType = 'general';
  selectedCategory: string = 'General';
  rating: number = 5;
  subject: string = '';
  message: string = '';
  contactEmail: string = '';
  contactName: string = '';

  isSubmitting = false;
  submittedSuccess = false;

  feedbackTypes = [
    { type: 'general' as FeedbackType, label: 'Feedback', icon: 'chatbubble-ellipses-outline', color: '#0284c7' },
    { type: 'bug_report' as FeedbackType, label: 'Bug Report', icon: 'bug-outline', color: '#dc2626' },
    { type: 'feature_request' as FeedbackType, label: 'Suggestion', icon: 'bulb-outline', color: '#7c3aed' },
    { type: 'content_issue' as FeedbackType, label: 'Content Issue', icon: 'book-outline', color: '#d97706' }
  ];

  categories = [
    'General',
    'Vocabulary',
    'News & Articles',
    'Coding Arena',
    'Daily Quizzes',
    'Brain Games',
    'Financial Wisdom',
    'Health & Habits',
    'Spiritual Section',
    'UI & Navigation'
  ];

  ratingLabels = ['Very Poor', 'Poor', 'Average', 'Good', 'Outstanding!'];

  constructor() {
    addIcons({
      arrowBack,
      paperPlaneOutline,
      star,
      starOutline,
      checkmarkCircle,
      bugOutline,
      bulbOutline,
      chatbubbleEllipsesOutline,
      bookOutline,
      informationCircleOutline,
      alertCircleOutline,
      sparklesOutline
    });
  }

  ngOnInit() {
    this.authService.currentUser$.subscribe(profile => {
      this.user = profile;
      if (profile) {
        this.contactEmail = profile.email || '';
        this.contactName = profile.name || '';
      }
    });
  }

  selectType(type: FeedbackType) {
    this.selectedType = type;
  }

  setRating(starValue: number) {
    this.rating = starValue;
  }

  getRatingLabel(): string {
    if (this.rating >= 1 && this.rating <= 5) {
      return this.ratingLabels[this.rating - 1];
    }
    return '';
  }

  getClientDeviceInfo(): string {
    const userAgent = navigator.userAgent;
    const screenWidth = window.screen.width;
    const screenHeight = window.screen.height;
    return `Browser: ${navigator.userAgent.substring(0, 100)} | Screen: ${screenWidth}x${screenHeight}`;
  }

  async submitFeedback() {
    if (!this.subject.trim()) {
      const toast = await this.toastCtrl.create({
        message: 'Please enter a subject or title for your feedback.',
        duration: 2500,
        color: 'warning',
        position: 'bottom'
      });
      toast.present();
      return;
    }

    if (!this.message.trim() || this.message.trim().length < 5) {
      const toast = await this.toastCtrl.create({
        message: 'Please provide a detailed description (at least 5 characters).',
        duration: 2500,
        color: 'warning',
        position: 'bottom'
      });
      toast.present();
      return;
    }

    if (!this.contactEmail.trim()) {
      const toast = await this.toastCtrl.create({
        message: 'Please provide an email address so we can follow up with you.',
        duration: 2500,
        color: 'warning',
        position: 'bottom'
      });
      toast.present();
      return;
    }

    const loading = await this.loadingCtrl.create({
      message: 'Sending feedback...',
      spinner: 'crescent'
    });
    await loading.present();
    this.isSubmitting = true;

    const payload = {
      feedback_type: this.selectedType,
      category: this.selectedCategory,
      subject: this.subject.trim(),
      message: this.message.trim(),
      rating: this.rating,
      user_email: this.contactEmail.trim(),
      user_name: this.contactName.trim() || (this.user?.name || undefined),
      device_info: this.getClientDeviceInfo()
    };

    this.feedbackService.submitFeedback(payload).subscribe({
      next: async (res) => {
        await loading.dismiss();
        this.isSubmitting = false;
        this.submittedSuccess = true;
        const toast = await this.toastCtrl.create({
          message: 'Thank you! Your feedback has been sent to our team.',
          duration: 3000,
          color: 'success',
          position: 'bottom'
        });
        toast.present();
      },
      error: async (err) => {
        await loading.dismiss();
        this.isSubmitting = false;
        console.error('Failed to submit feedback:', err);
        const toast = await this.toastCtrl.create({
          message: err?.error?.detail || 'Failed to submit feedback. Please try again.',
          duration: 3500,
          color: 'danger',
          position: 'bottom'
        });
        toast.present();
      }
    });
  }

  resetForm() {
    this.submittedSuccess = false;
    this.subject = '';
    this.message = '';
    this.rating = 5;
    this.selectedType = 'general';
    this.selectedCategory = 'General';
  }

  goBack() {
    this.router.navigate(['/profile']);
  }
}
