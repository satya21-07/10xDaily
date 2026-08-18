import { Injectable, inject } from '@angular/core';
import { AuthService } from './auth.service';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { catchError, tap } from 'rxjs/operators';
import { environment } from '../../environments/environment';

export interface SpiritualSource {
  name: string;
  scripture_type: string;
  reference: string;
  chapter?: number | null;
  verse?: number | null;
  kanda_or_parva?: string | null;
  character?: string | null;
  original_sanskrit?: string | null;
  transliteration?: string | null;
  translation: string;
  hindi_translation?: string | null;
  commentators?: Record<string, string> | null;
}


export interface SpiritualReflection {
  title: string;
  story_context?: string | null;
  explanation: string;
  key_takeaways: string[];
}

export interface TodayPractice {
  title: string;
  description: string;
}

export interface SpiritualLesson {
  lesson_date: string;
  day_number: number;
  total_days_or_verses: number;
  topic: string;
  source: SpiritualSource;
  reflection: SpiritualReflection;
  today_practice: TodayPractice;
  journal_prompt: string;
}

@Injectable({
  providedIn: 'root'
})
export class SpiritualService {
  private http = inject(HttpClient);
  private authService = inject(AuthService);
  private currentUserId: string | number | null = null;
  private apiUrl = `${environment.apiUrl}/spiritual`;

  private lessonCache = new Map<string, SpiritualLesson>();

  constructor() {
    this.authService.currentUser$.subscribe(user => {
      const newUserId = user?.id || null;
      if (this.currentUserId !== newUserId) {
        this.currentUserId = newUserId;
        this.lessonCache.clear();
      }
    });
  }

  getDailyLesson(
    scripture: string = 'gita',
    day?: number,
    chapter?: number,
    verse?: number,
    forceRefresh?: boolean
  ): Observable<SpiritualLesson> {
    const cacheKey = `${scripture}_${day || 'auto'}_${chapter || ''}_${verse || ''}`;

    if (!forceRefresh && this.lessonCache.has(cacheKey)) {
      return of(JSON.parse(JSON.stringify(this.lessonCache.get(cacheKey)!)));
    }

    let params = new HttpParams().set('scripture', scripture);
    if (day !== undefined && day !== null) {
      params = params.set('day', day.toString());
    }
    if (chapter !== undefined && chapter !== null) {
      params = params.set('chapter', chapter.toString());
    }
    if (verse !== undefined && verse !== null) {
      params = params.set('verse', verse.toString());
    }

    return this.http.get<SpiritualLesson>(`${this.apiUrl}/daily`, { params }).pipe(
      tap(lesson => {
        this.lessonCache.set(cacheKey, lesson);
      }),
      catchError(error => {
        console.error('Error fetching spiritual lesson, using offline fallback', error);
        return of(this.getOfflineMockData(scripture, day));
      })
    );
  }

  private getOfflineMockData(scripture: string, day?: number): SpiritualLesson {
    const today = new Date().toISOString().split('T')[0];
    
    if (scripture === 'character') {
      return {
        lesson_date: today,
        day_number: day || 1,
        total_days_or_verses: 23,
        topic: 'Character of the Day',
        source: {
          name: 'Wikipedia',
          scripture_type: 'character',
          reference: 'Arjuna',
          translation: 'Arjuna is a major character in the Indian epic Mahabharata. He was the third of the Pandava brothers and was known for his archery skills.',
        },
        reflection: {
          title: 'Who is Arjuna?',
          explanation: 'Arjuna is a major character in the Indian epic Mahabharata.',
          key_takeaways: ['Learn from the life and stories of Arjuna.']
        },
        today_practice: {
          title: 'Reflect on Character',
          description: 'Take a moment to read and reflect upon the values and stories associated with Arjuna.'
        },
        journal_prompt: 'What lessons can you draw from the mythology of Arjuna?'
      };
    }

    // Default to Gita
    return {
      lesson_date: today,
      day_number: day || 1,
      total_days_or_verses: 700,
      topic: 'Nishkama Karma',
      source: {
        name: 'Bhagavad Gita',
        scripture_type: 'gita',
        reference: 'Bhagavad Gita 2.47',
        chapter: 2,
        verse: 47,
        kanda_or_parva: 'Chapter 2',
        character: 'Krishna',
        original_sanskrit: 'धृतराष्ट्र उवाच |\nधर्मक्षेत्रे कुरुक्षेत्रे समवेता युयुत्सवः |\nमामकाः पाण्डवाश्चैव किमकुर्वत सञ्जय ||१-१||',
        transliteration: 'dhṛtarāṣṭra uvāca |\ndharmakṣetre kurukṣetre samavetā yuyutsavaḥ |\nmāmakāḥ pāṇḍavāścaiva kimakurvata sañjaya ||',
        translation: 'Dhritarashtra said: O Sanjaya, assembled on the holy field of Kurukshetra and eager for battle, what did my sons and the sons of Pandu do?',
        hindi_translation: 'धृतराष्ट्र ने कहा -- हे संजय ! धर्मभूमि कुरुक्षेत्र में एकत्र हुए युद्ध के इच्छुक मेरे और पाण्डु के पुत्रों ने क्या किया?',
        commentators: {
          'Gita Press': 'धर्मभूमि कुरुक्षेत्र में कर्म और कर्तव्य का उपदेश।'
        }
      },
      reflection: {
        title: 'Nishkama Karma — Action Without Attachment',
        story_context: 'On the battlefield of Kurukshetra, Shri Krishna teaches Arjuna how to act with excellence without being crippled by anxiety over outcomes.',
        explanation: 'In the second chapter of the Bhagavad Gita, Krishna delivers one of the most transformative teachings in world philosophy: we suffer because we are attached to outcomes rather than the quality of our effort. You have a right to act — but you do not own the outcome.',
        key_takeaways: [
          'Your duty is to act with full effort; the outcome is beyond your control',
          'Attachment to results distorts judgment and creates anxiety',
          'Detachment from outcomes leads to superior performance and inner peace'
        ]
      },
      today_practice: {
        title: 'One Task, Full Effort',
        description: 'Choose the most important task today. Before beginning, commit silently: "I will give this my complete focus and effort without worrying about the outcome."'
      },
      journal_prompt: 'Where in your life today would detachment from the outcome give you greater peace and clarity?'
    };
  }
}

