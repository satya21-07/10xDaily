import { Component, OnInit, inject } from '@angular/core';
import { CommonModule, Location } from '@angular/common';
import { IonicModule } from '@ionic/angular';
import { Router } from '@angular/router';
import { QuizService, QuizQuestion, QuizResponse } from '../../services/quiz.service';
import { AuthService } from '../../services/auth.service';
import { LoaderComponent } from '../../shared/components/loader/loader.component';
import { addIcons } from 'ionicons';
import { 
  checkmarkCircleOutline, closeCircleOutline, arrowForwardOutline, arrowBackOutline, 
  refreshOutline, homeOutline, trophyOutline, listOutline, chevronBackOutline, 
  bookmarkOutline, shareOutline, bulbOutline, bookOutline, cashOutline, 
  newspaperOutline, codeSlashOutline, leafOutline, checkmarkCircle, closeCircle
} from 'ionicons/icons';

export interface TopicPerformance {
  topic: string;
  correct: number;
  total: number;
}

@Component({
  selector: 'app-quiz',
  standalone: true,
  imports: [CommonModule, IonicModule, LoaderComponent],
  templateUrl: './quiz.component.html',
  styleUrls: ['./quiz.component.scss']
})
export class QuizComponent implements OnInit {
  private quizService = inject(QuizService);
  private authService = inject(AuthService);
  private router = inject(Router);
  private location = inject(Location);

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
  topicPerformanceList: TopicPerformance[] = [];
  
  private storageKey = '';

  constructor() {
    addIcons({ 
      checkmarkCircleOutline, closeCircleOutline, arrowForwardOutline, arrowBackOutline, 
      refreshOutline, homeOutline, trophyOutline, listOutline, chevronBackOutline, 
      bookmarkOutline, shareOutline, bulbOutline, bookOutline, cashOutline, 
      newspaperOutline, codeSlashOutline, leafOutline, checkmarkCircle, closeCircle
    });
  }

  private activeUserId: string | number = '';

  ngOnInit() {
    this.authService.currentUser$.subscribe(user => {
      const newUserId = user?.id || 'guest';
      this.activeUserId = newUserId;
      
      const today = new Date().toISOString().split('T')[0];
      const newStorageKey = `10xdaily_quiz_state_${newUserId}_${today}`;
      
      if (this.storageKey !== newStorageKey) {
        this.storageKey = newStorageKey;
        this.forceFullReset();
        this.loadQuiz(newUserId);
      }
    });
  }
  
  private forceFullReset() {
    this.questions = [];
    this.userAnswers = [];
    this.score = 0;
    this.currentIndex = 0;
    this.isFinished = false;
    this.isReviewing = false;
    this.statsSynced = false;
    this.selectedOptionIndex = null;
    this.isAnswerSubmitted = false;
    this.topicPerformanceList = [];
    this.isLoading = true;
  }

  loadQuiz(userId: string | number = this.activeUserId) {
    this.isLoading = true;
    this.quizService.getDailyQuiz().subscribe({
      next: (res: QuizResponse) => {
        // Prevent race condition if user changed while loading
        if (this.activeUserId !== userId) return;
        
        this.questions = res.questions || [];
        this.userAnswers = new Array(this.questions.length).fill(null);
        
        if (this.authService.isLoggedIn) {
          this.quizService.getTodayProgress().subscribe({
            next: (prog) => {
              if (prog.saved_state) {
                this.applyState(prog.saved_state);
              } else {
                this.loadStateFromStorage(); // Fallback to local storage for migration
              }
              this.isLoading = false;
            },
            error: () => {
              this.loadStateFromStorage();
              this.isLoading = false;
            }
          });
        } else {
          this.loadStateFromStorage();
          this.isLoading = false;
        }
      },
      error: (err) => {
        if (this.activeUserId !== userId) return;
        console.error('Failed to load quiz', err);
        this.isLoading = false;
      }
    });
  }

  private applyState(state: any) {
    const userAnswers = state.userAnswers || state.user_answers;
    const isFinished = state.isFinished !== undefined ? state.isFinished : state.is_finished;
    const statsSynced = state.statsSynced !== undefined ? state.statsSynced : state.stats_synced;
    
    if (userAnswers && userAnswers.length === this.questions.length) {
      this.userAnswers = userAnswers;
      this.score = state.score;
      this.isFinished = isFinished;
      this.statsSynced = statsSynced || false;
      
      if (this.isFinished) {
        this.calculateTopicPerformance();
      }

      if (this.isFinished && !this.statsSynced) {
        this.syncStats();
      }
      
      if (!this.isFinished && !this.isReviewing) {
        const firstUnanswered = this.userAnswers.findIndex((ans: any) => ans === null);
        this.currentIndex = firstUnanswered !== -1 ? firstUnanswered : 0;
      }
    }
  }

  private loadStateFromStorage() {
    if (typeof window !== 'undefined' && window.localStorage) {
      const savedState = localStorage.getItem(this.storageKey);
      if (savedState) {
        try {
          const state = JSON.parse(savedState);
          this.applyState(state);
        } catch (e) {
          console.error('Failed to parse quiz state');
        }
      }
    }
  }

  private saveStateToStorage() {
    const state = {
      userAnswers: this.userAnswers,
      score: this.score,
      isFinished: this.isFinished,
      statsSynced: this.statsSynced
    };
    
    if (typeof window !== 'undefined' && window.localStorage) {
      localStorage.setItem(this.storageKey, JSON.stringify(state));
    }

    if (this.authService.isLoggedIn) {
      this.quizService.saveProgress({
        user_answers: this.userAnswers,
        score: this.score,
        is_finished: this.isFinished,
        stats_synced: this.statsSynced
      }).subscribe();
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
    
    if (this.userAnswers[this.currentIndex] === null) {
      this.userAnswers[this.currentIndex] = this.selectedOptionIndex;
      const currentQ = this.questions[this.currentIndex];
      if (this.selectedOptionIndex === currentQ.correct_index) {
        this.score++;
      }
    } else {
      const currentQ = this.questions[this.currentIndex];
      const previousAnswer = this.userAnswers[this.currentIndex];
      
      if (previousAnswer === currentQ.correct_index && this.selectedOptionIndex !== currentQ.correct_index) {
        this.score--; 
      } else if (previousAnswer !== currentQ.correct_index && this.selectedOptionIndex === currentQ.correct_index) {
        this.score++; 
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
        this.calculateTopicPerformance();
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

  calculateTopicPerformance() {
    const perf: { [key: string]: { correct: number, total: number } } = {
        'Vocabulary': { correct: 0, total: 0 },
        'Finance': { correct: 0, total: 0 },
        'News': { correct: 0, total: 0 },
        'Coding': { correct: 0, total: 0 },
        'Spiritual': { correct: 0, total: 0 }
    };
    
    this.questions.forEach((q, i) => {
        const t = q.topic;
        if (!perf[t]) return;
        perf[t].total++;
        if (this.userAnswers[i] === q.correct_index) {
            perf[t].correct++;
        }
    });
    
    this.topicPerformanceList = [
        { topic: 'Vocabulary', ...perf['Vocabulary'] },
        { topic: 'Finance', ...perf['Finance'] },
        { topic: 'News', ...perf['News'] },
        { topic: 'Coding', ...perf['Coding'] },
        { topic: 'Spiritual', ...perf['Spiritual'] }
    ];
  }

  get accuracy(): number {
    const totalAnswered = this.userAnswers.filter(a => a !== null).length;
    if (totalAnswered === 0) return 0;
    return Math.round((this.score / totalAnswered) * 100);
  }

  goBack() {
    this.location.back();
  }

  goHome() {
    this.router.navigate(['/']);
  }

  getTopicIcon(topic: string): string {
    switch(topic) {
      case 'Vocabulary': return 'book-outline';
      case 'Finance': return 'cash-outline';
      case 'News': return 'newspaper-outline';
      case 'Coding': return 'code-slash-outline';
      case 'Spiritual': return 'leaf-outline';
      default: return 'list-outline';
    }
  }
}

