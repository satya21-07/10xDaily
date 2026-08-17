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
    verse?: number
  ): Observable<SpiritualLesson> {
    const cacheKey = `${scripture}_${day || 'auto'}_${chapter || ''}_${verse || ''}`;

    if (this.lessonCache.has(cacheKey)) {
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
    return {
      lesson_date: today,
      day_number: day || 1,
      total_days_or_verses: scripture === 'gita' ? 700 : 8,
      topic: scripture === 'ramayana' ? 'Ideal Human Being' : scripture === 'mahabharata' ? 'The Shield of Dharma' : 'Nishkama Karma',
      source: {
        name: scripture === 'ramayana' ? 'Valmiki Ramayana' : scripture === 'mahabharata' ? 'Vyasa Mahabharata' : 'Bhagavad Gita',
        scripture_type: scripture,
        reference: scripture === 'ramayana' ? 'Bala Kanda 1.1' : scripture === 'mahabharata' ? 'Adi Parva 1.267' : 'Bhagavad Gita 2.47',
        chapter: 2,
        verse: 47,
        kanda_or_parva: 'Chapter 2',
        character: 'Krishna',
        original_sanskrit: scripture === 'ramayana' ? 'तपस्स्वाध्यायनिरतां तपस्वी वाग्विदां वरम्।\nनारदं परिपप्रच्छ वाल्मीकिर्मुनिपुङ्गवम्॥' : scripture === 'mahabharata' ? 'नारायणं नमस्कृत्य नरं चैव नरोत्तमम्।\nदेवीं सरस्वतीं व्यासं ततो जयमुदीरयेत्॥' : 'धृतराष्ट्र उवाच |\nधर्मक्षेत्रे कुरुक्षेत्रे समवेता युयुत्सवः |\nमामकाः पाण्डवाश्चैव किमकुर्वत सञ्जय ||१-१||',
        transliteration: scripture === 'ramayana' ? 'tapassvādhyāyaniratāṁ tapasvī vāgvidāṁ varam |\nnāradaṁ paripapraccha vālmīkirmunipuṅgavam ||' : scripture === 'mahabharata' ? 'nārāyaṇaṁ namaskṛtya naraṁ caiva narottamam |\ndevīṁ sarasvatīṁ vyāsaṁ tato jayamudīrayet ||' : 'dhṛtarāṣṭra uvāca |\ndharmakṣetre kurukṣetre samavetā yuyutsavaḥ |\nmāmakāḥ pāṇḍavāścaiva kimakurvata sañjaya ||',
        translation: scripture === 'ramayana' ? 'Valmiki asked sage Narada: Who in this world is truly virtuous, heroic, righteous, grateful, truthful, and resolute in vows?' : scripture === 'mahabharata' ? 'Having bowed down in deep reverence to Lord Narayana, to Nara, Goddess Sarasvati, and Sage Vyasa, let the epic of Jaya be proclaimed.' : 'Dhritarashtra said: O Sanjaya, assembled on the holy field of Kurukshetra and eager for battle, what did my sons and the sons of Pandu do?',
        hindi_translation: scripture === 'ramayana' ? 'तपस्वी महर्षि वाल्मीकि ने तप और स्वाध्याय में निरन्तर लगे रहने वाले, वाणी के ज्ञाताओं में श्रेष्ठ मुनिवर नारद जी से पूछा: इस संसार में ऐसा कौन सा गुणवान, पराक्रमी, धर्मज्ञ, कृतज्ञ, सत्यवादी और दृढ़प्रतिज्ञ पुरुष है जो सब प्राणियों का हितैषी हो?' : scripture === 'mahabharata' ? 'भगवान नारायण (श्रीहरि), नरों में श्रेष्ठ नर (अर्जुन), भगवती सरस्वती देवी और महर्षि वेदव्यास को श्रद्धापूर्वक नमस्कार करके जय (महाभारत ग्रंथ) का पाठ प्रारम्भ करना चाहिए।' : 'धृतराष्ट्र ने कहा -- हे संजय ! धर्मभूमि कुरुक्षेत्र में एकत्र हुए युद्ध के इच्छुक मेरे और पाण्डु के पुत्रों ने क्या किया?',
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

