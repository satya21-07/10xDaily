import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { catchError, tap } from 'rxjs/operators';
import { environment } from '../../environments/environment';

export interface CodingConcept {
  title: string;
  explanation: string;
  key_points: string[];
  example: string;
}

export interface CodingQuestion {
  id: string;
  title: string;
  description: string;
  difficulty: string;
  pattern: string;
  tags: string[];
  hint: string;
  approach: string;
  explanation: string;
  time_complexity: string;
  space_complexity: string;
  solution_java?: string;
  solution_python?: string;
  solution_javascript?: string;
  solution_cpp?: string;
}

export interface CodingLesson {
  topic: string;
  learning_objective: string;
  concepts: CodingConcept[];
  questions: CodingQuestion[];
}

@Injectable({
  providedIn: 'root'
})
export class CodingService {
  private http = inject(HttpClient);
  private apiUrl = `${environment.apiUrl}/coding`;

  private cachedLesson: CodingLesson | null = null;
  private cacheDate: string | null = null;

  getDailyLesson(): Observable<CodingLesson> {
    const today = new Date().toISOString().split('T')[0];
    
    if (this.cachedLesson && this.cacheDate === today) {
      return of(this.cachedLesson);
    }
    
    return this.http.get<CodingLesson>(`${this.apiUrl}/daily`).pipe(
      tap(lesson => {
        this.cachedLesson = lesson;
        this.cacheDate = today;
      }),
      catchError(error => {
        console.error('Error fetching coding lesson, using offline fallback', error);
        return of(this.getOfflineMockData());
      })
    );
  }

  private getOfflineMockData(): CodingLesson {
    return {
      topic: "Offline Fallback: Sliding Window",
      learning_objective: "Understand how the sliding window technique can reduce repeated traversal of contiguous elements.",
      concepts: [
        {
          title: "What is a Sliding Window?",
          explanation: "A sliding window is a sublist that runs over an underlying collection.",
          key_points: [
            "It avoids redundant work in nested loops.",
            "Typically used for contiguous subarrays or substrings.",
            "Can be fixed size or dynamically resizing."
          ],
          example: "Finding the maximum sum of any contiguous subarray of size k."
        }
      ],
      questions: [
        {
          id: "q1-sw",
          title: "Maximum Subarray Average",
          description: "Given an array of integers nums and an integer k, find the contiguous subarray of length k that has the maximum average value and return this value.",
          difficulty: "Easy",
          pattern: "Sliding Window",
          tags: ["Array", "Sliding Window"],
          hint: "Calculate the sum of the first k elements. Then, slide the window by subtracting the element going out and adding the element coming in.",
          approach: "We can maintain a running sum of the current window of size k. As the window slides to the right, we update the sum in O(1) time.",
          explanation: "This approach avoids recalculating the sum from scratch for every window, reducing the time complexity from O(N*K) to O(N).",
          time_complexity: "O(N)",
          space_complexity: "O(1)",
          solution_java: "class Solution { ... }",
          solution_python: "class Solution: ...",
          solution_javascript: "var findMaxAverage = function(nums, k) { ... };",
          solution_cpp: "class Solution { ... };"
        }
      ]
    };
  }
}
