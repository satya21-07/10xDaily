import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { IonicModule } from '@ionic/angular';
import { Router } from '@angular/router';
import { QuizService, QuizQuestion, QuizResponse } from '../../services/quiz.service';
import { AuthService } from '../../services/auth.service';
import { addIcons } from 'ionicons';
import { checkmarkCircleOutline, closeCircleOutline, arrowForwardOutline, arrowBackOutline, refreshOutline, homeOutline, trophyOutline, listOutline } from 'ionicons/icons';

@Component({
  selector: 'app-quiz',
  standalone: true,
  imports: [CommonModule, IonicModule],
  templateUrl: './quiz.component.html',
  styleUrls: ['./quiz.component.scss']
})
export class QuizComponent implements OnInit {
  private quizService = inject(QuizService);
  private authService = inject(AuthService);
  private router = inject(Router);

  isLoading = true;
  questions: QuizQuestion[] = [];
  currentIndex = 0;
  score = 0;
  
  selectedOptionIndex: number | null = null;
  isAnswerSubmitted = false;
  isFinished = false;
  
  // New state for persistence and review
  userAnswers: (number | null)[] = [];
  isReviewing = false;
  statsSynced = false;
  
  private storageKey = '';

  constructor() {
    addIcons({ checkmarkCircleOutline, closeCircleOutline, arrowForwardOutline, arrowBackOutline, refreshOutline, homeOutline, trophyOutline, listOutline });
  }

  ngOnInit() {
    const today = new Date().toISOString().split('T')[0];
    this.storageKey = `10xdaily_quiz_state_${today}`;
    this.loadQuiz();
  }

  loadQuiz() {
    this.isLoading = true;
    this.quizService.getDailyQuiz().subscribe({
      next: (res: QuizResponse) => {
        this.questions = res.questions || [];
        this.userAnswers = new Array(this.questions.length).fill(null);
        this.loadStateFromStorage();
        this.isLoading = false;
      },
      error: (err) => {
        console.error('Failed to load quiz', err);
        this.isLoading = false;
      }
    });
  }

  private loadStateFromStorage() {
    if (typeof window !== 'undefined' && window.localStorage) {
      const savedState = localStorage.getItem(this.storageKey);
      if (savedState) {
        try {
          const state = JSON.parse(savedState);
          this.userAnswers = state.userAnswers;
          this.score = state.score;
          this.isFinished = state.isFinished;
          this.statsSynced = state.statsSynced || false;
          
          if (this.isFinished && !this.statsSynced) {
            // Retroactively sync stats if they finished before this feature existed
            this.syncStats();
          }
          
          if (!this.isFinished && !this.isReviewing) {
            // Find the first unanswered question
            const firstUnanswered = this.userAnswers.findIndex(ans => ans === null);
            this.currentIndex = firstUnanswered !== -1 ? firstUnanswered : 0;
          }
        } catch (e) {
          console.error('Failed to parse quiz state');
        }
      }
    }
  }

  private saveStateToStorage() {
    if (typeof window !== 'undefined' && window.localStorage) {
      const state = {
        userAnswers: this.userAnswers,
        score: this.score,
        isFinished: this.isFinished,
        statsSynced: this.statsSynced
      };
      localStorage.setItem(this.storageKey, JSON.stringify(state));
    }
  }

  selectOption(index: number) {
    if (this.isAnswerSubmitted || this.isReviewing) return;
    this.selectedOptionIndex = index;
    this.submitAnswer();
  }

  submitAnswer() {
    if (this.selectedOptionIndex === null) return;
    
    this.isAnswerSubmitted = true;
    
    // Only increase score if it's the first time answering this question
    if (this.userAnswers[this.currentIndex] === null) {
      this.userAnswers[this.currentIndex] = this.selectedOptionIndex;
      const currentQ = this.questions[this.currentIndex];
      if (this.selectedOptionIndex === currentQ.correct_index) {
        this.score++;
      }
    } else {
      // Overwrite previous answer, adjust score if necessary
      const currentQ = this.questions[this.currentIndex];
      const previousAnswer = this.userAnswers[this.currentIndex];
      
      if (previousAnswer === currentQ.correct_index && this.selectedOptionIndex !== currentQ.correct_index) {
        this.score--; // Changed from right to wrong
      } else if (previousAnswer !== currentQ.correct_index && this.selectedOptionIndex === currentQ.correct_index) {
        this.score++; // Changed from wrong to right
      }
      this.userAnswers[this.currentIndex] = this.selectedOptionIndex;
    }
    
    this.saveStateToStorage();
  }

  nextQuestion() {
    if (this.currentIndex < this.questions.length - 1) {
      this.currentIndex++;
      
      if (this.userAnswers[this.currentIndex] !== null) {
        this.selectedOptionIndex = this.userAnswers[this.currentIndex];
        this.isAnswerSubmitted = true;
      } else {
        this.selectedOptionIndex = null;
        this.isAnswerSubmitted = false;
      }
    } else {
      if (this.isReviewing) {
        this.isReviewing = false;
      }
      
      if (!this.isFinished) {
        this.isFinished = true;
      }
      
      if (!this.statsSynced) {
        this.syncStats();
      }
      
      this.saveStateToStorage();
    }
  }

  private syncStats() {
    if (this.authService.isLoggedIn) {
      const validAnswersCount = this.userAnswers.filter(a => a !== null).length;
      this.authService.updateStats({
        quiz_correct_increment: this.score,
        quiz_total_increment: validAnswersCount,
        modules_completed_increment: (this.score / validAnswersCount) >= 0.7 ? 1 : 0
      }).subscribe(() => {
        this.statsSynced = true;
        this.saveStateToStorage();
      });
    }
  }

  previousQuestion() {
    if (this.currentIndex > 0) {
      this.currentIndex--;
      
      if (this.userAnswers[this.currentIndex] !== null) {
        this.selectedOptionIndex = this.userAnswers[this.currentIndex];
        this.isAnswerSubmitted = true;
      } else {
        this.selectedOptionIndex = null;
        this.isAnswerSubmitted = false;
      }
    }
  }

  getOptionClass(index: number): string {
    if (!this.isAnswerSubmitted && !this.isReviewing) {
      return this.selectedOptionIndex === index ? 'selected' : '';
    }
    
    const currentQ = this.questions[this.currentIndex];
    const answeredIndex = this.isReviewing ? this.userAnswers[this.currentIndex] : this.selectedOptionIndex;
    
    if (index === currentQ.correct_index) {
      return 'correct';
    }
    if (index === answeredIndex && index !== currentQ.correct_index) {
      return 'incorrect';
    }
    return 'disabled';
  }
  
  startReview() {
    this.isReviewing = true;
    this.isFinished = false;
    this.currentIndex = 0;
    this.selectedOptionIndex = this.userAnswers[0];
    this.isAnswerSubmitted = true;
  }
  
  resetQuiz() {
    if (typeof window !== 'undefined' && window.localStorage) {
      localStorage.removeItem(this.storageKey);
    }
    this.userAnswers = new Array(this.questions.length).fill(null);
    this.score = 0;
    this.currentIndex = 0;
    this.isFinished = false;
    this.isReviewing = false;
    this.statsSynced = false;
    this.selectedOptionIndex = null;
    this.isAnswerSubmitted = false;
  }
}
