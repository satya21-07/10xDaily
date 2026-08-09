import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { catchError, tap } from 'rxjs/operators';
import { environment } from '../../environments/environment';

export interface FinanceConcept {
  title: string;
  explanation: string;
}

export interface FinanceExample {
  title: string;
  explanation: string;
}

export interface FinanceActionItem {
  title: string;
  description: string;
}

export interface FinanceLesson {
  topic: string;
  why_it_matters: string;
  concepts: FinanceConcept[];
  example: FinanceExample;
  common_mistake: string;
  action_item: FinanceActionItem;
  reflection: string;
  disclaimer: string;
}

@Injectable({
  providedIn: 'root'
})
export class FinanceService {
  private http = inject(HttpClient);
  private apiUrl = `${environment.apiUrl}/finance`;

  private cachedLesson: { [country: string]: FinanceLesson } = {};
  private cacheDate: { [country: string]: string } = {};

  getDailyLesson(country: string = 'IN'): Observable<FinanceLesson> {
    const today = new Date().toISOString().split('T')[0];
    
    if (this.cachedLesson[country] && this.cacheDate[country] === today) {
      return of(this.cachedLesson[country]);
    }
    
    const params = new HttpParams().set('country', country);
    
    return this.http.get<FinanceLesson>(`${this.apiUrl}/daily`, { params }).pipe(
      tap(lesson => {
        this.cachedLesson[country] = lesson;
        this.cacheDate[country] = today;
      }),
      catchError(error => {
        console.error(`Error fetching finance lesson for ${country}, using offline fallback`, error);
        return of(this.getOfflineMockData(country));
      })
    );
  }

  // Calculators
  calculateCompoundInterest(params: { principal: number, annual_rate: number, years: number, compounding_frequency?: number }): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/calculator/compound-interest`, {
      compounding_frequency: 12,
      ...params
    });
  }

  calculateSIP(params: { monthly_investment: number, annual_return: number, years: number }): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/calculator/sip`, params);
  }

  calculateEMI(params: { principal: number, annual_interest_rate: number, tenure_months: number }): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/calculator/emi`, params);
  }

  calculateLoanInterest(params: { principal: number, annual_interest_rate: number, tenure_years: number, compounding_frequency?: number }): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/calculator/loan-interest`, {
      compounding_frequency: 12,
      ...params
    });
  }

  calculateInflation(params: { current_amount: number, inflation_rate: number, years: number }): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/calculator/inflation`, params);
  }

  calculateFutureValue(params: { present_value: number, annual_rate: number, years: number }): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/calculator/future-value`, params);
  }

  calculateRetirementCorpus(params: {
    current_age: number,
    retirement_age: number,
    life_expectancy: number,
    current_monthly_expenses: number,
    annual_inflation: number,
    post_retirement_return: number
  }): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/calculator/retirement-corpus`, params);
  }

  calculateEmergencyFund(params: { monthly_expenses: number, custom_months?: number }): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/calculator/emergency-fund`, {
      custom_months: 6,
      ...params
    });
  }

  private getOfflineMockData(country: string): FinanceLesson {
    const isIndia = country.toUpperCase() === 'IN';
    return {
      topic: "Compounding (Offline Fallback)",
      why_it_matters: "Compounding is the engine of long-term wealth creation, turning small consistent savings into a substantial corpus over time.",
      concepts: [
        {
          title: "What is Compounding?",
          explanation: "Compounding is earning interest on interest. When your investments generate earnings, those earnings are reinvested to generate their own earnings."
        },
        {
          title: "The Power of Time",
          explanation: "The longer your money stays invested, the faster it grows. Starting early is the single most important factor."
        }
      ],
      example: {
        title: "The Impact of Starting Early",
        explanation: isIndia 
          ? "Investing ₹5,000 monthly at an assumed 12% annual return grows to approximately ₹49.9 Lakh after 20 years, with ₹12 Lakh principal and ₹37.9 Lakh returns."
          : "Investing $100 monthly at an assumed 10% annual return grows to approximately $72,000 after 20 years."
      },
      common_mistake: "Waiting too long to start saving, or withdrawing compounding assets to fund discretionary purchases.",
      action_item: {
        title: isIndia ? "Start an Auto-Invest SIP" : "Start an Auto-Invest Plan",
        description: isIndia
          ? "Set up a small, automated monthly transfer of ₹5,000 (or what fits your budget) into an equity index mutual fund."
          : "Set up a small, automated transfer of $100 monthly into a low-cost stock index fund."
      },
      reflection: "How would starting your savings journey 5 years earlier have changed your security level today?",
      disclaimer: "For educational purposes only. This is not financial advice."
    };
  }
}
