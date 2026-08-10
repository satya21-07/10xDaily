import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { IonicModule } from '@ionic/angular';
import { RouterLink } from '@angular/router';
import { CodingService, CodingLesson } from '../../services/coding.service';
import { addIcons } from 'ionicons';
import { arrowBack, bulbOutline, codeSlashOutline, flashOutline, chevronDownOutline, chevronUpOutline, bookmarkOutline, bookmark,searchOutline, personCircleOutline } from 'ionicons/icons';
import { LoaderComponent } from '../../shared/components/loader/loader.component';
import { ProgressService } from '../../services/progress.service';
import { BookmarkService, Bookmark } from '../../core/services/bookmark.service';

@Component({
  selector: 'app-coding',
  standalone: true,
  imports: [IonicModule, CommonModule, RouterLink, LoaderComponent],
  templateUrl: './coding.component.html',
  styleUrls: ['./coding.component.scss'],
  host: { 'class': 'ion-page' }
})
export class CodingComponent implements OnInit {
  private codingService = inject(CodingService);
  private progressService = inject(ProgressService);
  private bookmarkService = inject(BookmarkService);
  
  lesson: CodingLesson | null = null;
  savedBookmarks: Bookmark[] = [];
  isLoading = true;
  expandedConceptIndex = 0;
  expandedQuestionIndex = -1;
  expandedSolutionIndex = -1;
  expandedApproachIndex = -1;
  activeSolutionTab: { [key: number]: 'java' | 'python' | 'javascript' | 'cpp' } = {};

  constructor() {
    addIcons({ arrowBack, bulbOutline, codeSlashOutline, flashOutline, chevronDownOutline, chevronUpOutline, bookmarkOutline, bookmark, searchOutline, personCircleOutline });
  }

  ngOnInit() {
    this.progressService.markVisited('coding');
    this.isLoading = true;
    this.codingService.getDailyLesson().subscribe({
      next: (data) => {
        this.lesson = data;
        this.isLoading = false;
      },
      error: () => {
        this.isLoading = false;
      }
    });
    this.loadBookmarks();
  }

  ionViewWillEnter() {
    this.loadBookmarks();
  }

  loadBookmarks() {
    this.bookmarkService.getBookmarks().subscribe(data => {
      this.savedBookmarks = data.filter(b => b.content_type === 'coding');
    });
  }

  isSaved(question: any): boolean {
    return this.savedBookmarks.some(b => b.title === question.title);
  }

  toggleSaveQuestion(question: any, event: Event) {
    event.stopPropagation();
    const existing = this.savedBookmarks.find(b => b.title === question.title);
    
    if (existing && existing.id) {
      this.bookmarkService.deleteBookmark(existing.id).subscribe(() => {
        this.loadBookmarks();
      });
    } else {
      this.bookmarkService.saveBookmark({
        title: question.title,
        content_type: 'coding',
        url: question.description,
        details: JSON.stringify(question)
      }).subscribe(() => {
        this.loadBookmarks();
      });
    }
  }

  loadLesson(event?: any) {
    this.isLoading = true;
    this.codingService.getDailyLesson().subscribe({
      next: (data) => {
        this.lesson = data;
        // Reset tabs default to Java
        if (data.questions) {
          data.questions.forEach((_, i) => this.activeSolutionTab[i] = 'java');
        }
        this.isLoading = false;
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

  toggleQuestion(index: number) {
    this.expandedQuestionIndex = this.expandedQuestionIndex === index ? -1 : index;
  }
  
  toggleSolution(index: number) {
    this.expandedSolutionIndex = this.expandedSolutionIndex === index ? -1 : index;
  }

  toggleApproach(index: number) {
    this.expandedApproachIndex = this.expandedApproachIndex === index ? -1 : index;
  }

  setSolutionTab(index: number, tab: 'java' | 'python' | 'javascript' | 'cpp') {
    this.activeSolutionTab[index] = tab;
  }
}
