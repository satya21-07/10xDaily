import { Component, OnInit, inject } from '@angular/core';
import { IonicModule } from '@ionic/angular';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { FinanceService, FinanceLesson } from '../../services/finance.service';
import { addIcons } from 'ionicons';
import { 
  arrowBack, walletOutline, trendingUpOutline, cashOutline, 
  chevronDownOutline, chevronUpOutline, bookmarkOutline, bookmark, 
  globeOutline, calculatorOutline, informationCircleOutline, warningOutline,
  statsChartOutline, alarmOutline, timeOutline, shieldCheckmarkOutline, personCircleOutline
} from 'ionicons/icons';
import { LoaderComponent } from '../../shared/components/loader/loader.component';
import { ProgressService } from '../../services/progress.service';
import { BookmarkService, Bookmark } from '../../core/services/bookmark.service';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-finance',
  standalone: true,
  imports: [IonicModule, CommonModule, RouterLink, FormsModule, LoaderComponent],
  templateUrl: './finance.component.html',
  styleUrls: ['./finance.component.scss'],
  host: { 'class': 'ion-page' }
})
export class FinanceComponent implements OnInit {
  private financeService = inject(FinanceService);
  private progressService = inject(ProgressService);
  private bookmarkService = inject(BookmarkService);
  private authService = inject(AuthService);
  
  private currentUserId: number | string = 'guest';
  
  lesson?: FinanceLesson;
  savedBookmarks: Bookmark[] = [];
  isLoading = true;
  expandedConceptIndex = 0;

  // Segment and selector states
  activeSegment: 'lesson' | 'calculators' = 'lesson';
  selectedCalculator = 'sip';
  countryCode = 'IN';
  currencySymbol = '₹';

  // Calculator states & results
  isCalculating = false;
  
  // SIP
  sipAmount = 5000;
  sipReturn = 12;
  sipYears = 20;
  sipResult: any = null;

  // EMI
  emiPrincipal = 1000000;
  emiInterest = 8.5;
  emiMonths = 120;
  emiResult: any = null;

  // Compound Interest
  ciPrincipal = 100000;
  ciRate = 8;
  ciYears = 10;
  ciFreq = 12;
  ciResult: any = null;

  // Loan Interest
  loanPrincipal = 500000;
  loanRate = 9;
  loanYears = 5;
  loanFreq = 12;
  loanResult: any = null;

  // Inflation
  infAmount = 50000;
  infRate = 6;
  infYears = 10;
  infResult: any = null;

  // Future Value
  fvPresent = 100000;
  fvRate = 8;
  fvYears = 10;
  fvResult: any = null;

  // Retirement Corpus
  retCurrentAge = 30;
  retRetireAge = 60;
  retLifeExpectancy = 85;
  retExpenses = 50000;
  retInflation = 6;
  retPostReturn = 8;
  retResult: any = null;

  // Emergency Fund
  emExpenses = 30000;
  emMonths = 6;
  emResult: any = null;

  constructor() {
    addIcons({ 
      arrowBack, walletOutline, trendingUpOutline, cashOutline, 
      chevronDownOutline, chevronUpOutline, bookmarkOutline, bookmark, 
      globeOutline, calculatorOutline, informationCircleOutline, warningOutline,
      statsChartOutline, alarmOutline, timeOutline, shieldCheckmarkOutline, personCircleOutline
    });
  }

  ngOnInit() {
    this.authService.currentUser$.subscribe(user => {
      const newUserId = user?.id || 'guest';
      if (this.currentUserId !== newUserId) {
        this.currentUserId = newUserId;
        this.resetState();
      }
      this.loadData();
    });
  }

  private loadData() {
    this.progressService.markVisited('finance');
    this.updateCurrencySymbol();
    this.loadLesson();
    this.loadBookmarks();
    this.calculateCurrent(); // Run initial calculation
  }

  private resetState() {
    this.expandedConceptIndex = 0;
    this.activeSegment = 'lesson';
    this.selectedCalculator = 'sip';
    this.isCalculating = false;
    
    // SIP
    this.sipAmount = 5000;
    this.sipReturn = 12;
    this.sipYears = 20;
    this.sipResult = null;

    // EMI
    this.emiPrincipal = 1000000;
    this.emiInterest = 8.5;
    this.emiMonths = 120;
    this.emiResult = null;

    // Compound Interest
    this.ciPrincipal = 100000;
    this.ciRate = 8;
    this.ciYears = 10;
    this.ciFreq = 12;
    this.ciResult = null;

    // Loan Interest
    this.loanPrincipal = 500000;
    this.loanRate = 9;
    this.loanYears = 5;
    this.loanFreq = 12;
    this.loanResult = null;

    // Inflation
    this.infAmount = 50000;
    this.infRate = 6;
    this.infYears = 10;
    this.infResult = null;

    // Future Value
    this.fvPresent = 100000;
    this.fvRate = 8;
    this.fvYears = 10;
    this.fvResult = null;

    // Retirement Corpus
    this.retCurrentAge = 30;
    this.retRetireAge = 60;
    this.retLifeExpectancy = 85;
    this.retExpenses = 50000;
    this.retInflation = 6;
    this.retPostReturn = 8;
    this.retResult = null;

    // Emergency Fund
    this.emExpenses = 30000;
    this.emMonths = 6;
    this.emResult = null;
    
    if (this.countryCode !== 'IN') {
      this.onCountryChange(); // To reset country-specific defaults
    } else {
      this.calculateCurrent();
    }
  }

  ionViewWillEnter() {
    this.loadBookmarks();
  }

  updateCurrencySymbol() {
    if (this.countryCode === 'IN') {
      this.currencySymbol = '₹';
    } else if (this.countryCode === 'US') {
      this.currencySymbol = '$';
    } else if (this.countryCode === 'GB') {
      this.currencySymbol = '£';
    } else {
      this.currencySymbol = '¤';
    }
  }

  onCountryChange() {
    this.updateCurrencySymbol();
    this.loadLesson();
    
    // Adjust calculator defaults based on country
    if (this.countryCode === 'IN') {
      this.sipAmount = 5000;
      this.emiPrincipal = 1000000;
      this.ciPrincipal = 100000;
      this.loanPrincipal = 500000;
      this.infAmount = 50000;
      this.fvPresent = 100000;
      this.retExpenses = 50000;
      this.emExpenses = 30000;
    } else {
      this.sipAmount = 250;
      this.emiPrincipal = 50000;
      this.ciPrincipal = 10000;
      this.loanPrincipal = 25000;
      this.infAmount = 5000;
      this.fvPresent = 10000;
      this.retExpenses = 3000;
      this.emExpenses = 2500;
    }
    
    this.calculateCurrent();
  }

  loadBookmarks() {
    this.bookmarkService.getBookmarks(true).subscribe(data => {
      this.savedBookmarks = (data || []).filter(b => b.content_type === 'finance');
    });
  }

  getEncodedTopic(topic: string): string {
    return encodeURIComponent(topic || 'Finance');
  }

  isSaved(concept: any): boolean {
    return this.savedBookmarks.some(b => b.title === concept.title);
  }

  toggleSaveConcept(concept: any, event: Event) {
    event.stopPropagation();
    const existing = this.savedBookmarks.find(b => b.title === concept.title);
    
    if (existing && existing.id) {
      this.bookmarkService.deleteBookmark(existing.id).subscribe(() => {
        this.loadBookmarks();
      });
    } else {
      this.bookmarkService.saveBookmark({
        title: concept.title,
        content_type: 'finance',
        url: concept.explanation || concept.description || '',
        details: JSON.stringify(concept)
      }).subscribe(() => {
        this.loadBookmarks();
      });
    }
  }

  loadLesson(event?: any) {
    this.isLoading = true;
    this.financeService.getDailyLesson(this.countryCode).subscribe({
      next: (data) => {
        this.lesson = data;
        this.isLoading = false;
        this.expandedConceptIndex = 0;
        if (event) {
          event.target.complete();
        }
      },
      error: () => {
        this.isLoading = false;
        if (event) {
          event.target.complete();
        }
      }
    });
  }

  toggleConcept(index: number) {
    this.expandedConceptIndex = this.expandedConceptIndex === index ? -1 : index;
  }

  // Calculator triggers
  calculateCurrent() {
    this.isCalculating = true;
    switch(this.selectedCalculator) {
      case 'sip':
        this.financeService.calculateSIP({
          monthly_investment: this.sipAmount,
          annual_return: this.sipReturn,
          years: this.sipYears
        }).subscribe({
          next: (res) => { this.sipResult = res; this.isCalculating = false; },
          error: () => { this.isCalculating = false; }
        });
        break;
      case 'emi':
        this.financeService.calculateEMI({
          principal: this.emiPrincipal,
          annual_interest_rate: this.emiInterest,
          tenure_months: this.emiMonths
        }).subscribe({
          next: (res) => { this.emiResult = res; this.isCalculating = false; },
          error: () => { this.isCalculating = false; }
        });
        break;
      case 'compound-interest':
        this.financeService.calculateCompoundInterest({
          principal: this.ciPrincipal,
          annual_rate: this.ciRate,
          years: this.ciYears,
          compounding_frequency: this.ciFreq
        }).subscribe({
          next: (res) => { this.ciResult = res; this.isCalculating = false; },
          error: () => { this.isCalculating = false; }
        });
        break;
      case 'loan-interest':
        this.financeService.calculateLoanInterest({
          principal: this.loanPrincipal,
          annual_interest_rate: this.loanRate,
          tenure_years: this.loanYears,
          compounding_frequency: this.loanFreq
        }).subscribe({
          next: (res) => { this.loanResult = res; this.isCalculating = false; },
          error: () => { this.isCalculating = false; }
        });
        break;
      case 'inflation':
        this.financeService.calculateInflation({
          current_amount: this.infAmount,
          inflation_rate: this.infRate,
          years: this.infYears
        }).subscribe({
          next: (res) => { this.infResult = res; this.isCalculating = false; },
          error: () => { this.isCalculating = false; }
        });
        break;
      case 'future-value':
        this.financeService.calculateFutureValue({
          present_value: this.fvPresent,
          annual_rate: this.fvRate,
          years: this.fvYears
        }).subscribe({
          next: (res) => { this.fvResult = res; this.isCalculating = false; },
          error: () => { this.isCalculating = false; }
        });
        break;
      case 'retirement-corpus':
        this.financeService.calculateRetirementCorpus({
          current_age: this.retCurrentAge,
          retirement_age: this.retRetireAge,
          life_expectancy: this.retLifeExpectancy,
          current_monthly_expenses: this.retExpenses,
          annual_inflation: this.retInflation,
          post_retirement_return: this.retPostReturn
        }).subscribe({
          next: (res) => { this.retResult = res; this.isCalculating = false; },
          error: () => { this.isCalculating = false; }
        });
        break;
      case 'emergency-fund':
        this.financeService.calculateEmergencyFund({
          monthly_expenses: this.emExpenses,
          custom_months: this.emMonths
        }).subscribe({
          next: (res) => { this.emResult = res; this.isCalculating = false; },
          error: () => { this.isCalculating = false; }
        });
        break;
      default:
        this.isCalculating = false;
    }
  }

  navigateToCalculatorForTopic() {
    const topic = this.lesson?.topic.toLowerCase() || '';
    if (topic.includes('emergency')) {
      this.selectedCalculator = 'emergency-fund';
      this.emExpenses = this.countryCode === 'IN' ? 30000 : 2500;
    } else if (topic.includes('sip') || topic.includes('mutual') || topic.includes('index') || topic.includes('investing')) {
      this.selectedCalculator = 'sip';
      this.sipAmount = this.countryCode === 'IN' ? 5000 : 250;
    } else if (topic.includes('emi') || topic.includes('debt') || topic.includes('loan') || topic.includes('credit')) {
      this.selectedCalculator = 'emi';
      this.emiPrincipal = this.countryCode === 'IN' ? 1000000 : 50000;
    } else if (topic.includes('compound') || topic.includes('time')) {
      this.selectedCalculator = 'compound-interest';
      this.ciPrincipal = this.countryCode === 'IN' ? 100000 : 10000;
    } else if (topic.includes('inflation') || topic.includes('purchasing') || topic.includes('power')) {
      this.selectedCalculator = 'inflation';
      this.infAmount = this.countryCode === 'IN' ? 50000 : 5000;
    } else if (topic.includes('retirement') || topic.includes('nps') || topic.includes('epf') || topic.includes('ppf')) {
      this.selectedCalculator = 'retirement-corpus';
      this.retExpenses = this.countryCode === 'IN' ? 50000 : 3000;
    } else {
      this.selectedCalculator = 'sip';
    }
    
    this.activeSegment = 'calculators';
    this.calculateCurrent();
  }
}
