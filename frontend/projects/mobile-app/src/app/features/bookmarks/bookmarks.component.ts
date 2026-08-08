import { Component, OnInit } from '@angular/core';
import { IonicModule } from '@ionic/angular';
import { CommonModule } from '@angular/common';
import { BookmarkService, Bookmark } from '../../core/services/bookmark.service';

@Component({
  selector: 'app-bookmarks',
  standalone: true,
  imports: [IonicModule, CommonModule],
  templateUrl: './bookmarks.component.html',
  styleUrl: './bookmarks.component.scss'
})
export class BookmarksComponent implements OnInit {
  bookmarks: Bookmark[] = [];
  groupedBookmarks: { [key: string]: Bookmark[] } = {};
  topics: string[] = [];

  constructor(private bookmarkService: BookmarkService) {}

  ngOnInit() {
    this.loadBookmarks();
  }

  ionViewWillEnter() {
    this.loadBookmarks();
  }

  loadBookmarks() {
    this.bookmarkService.getBookmarks().subscribe({
      next: (data) => {
        this.bookmarks = data;
        this.groupBookmarks();
      },
      error: (err) => console.error('Error fetching bookmarks:', err)
    });
  }

  groupBookmarks() {
    this.groupedBookmarks = {};
    this.bookmarks.forEach((b: any) => {
      const type = b.content_type || 'Other';
      if (!this.groupedBookmarks[type]) {
        this.groupedBookmarks[type] = [];
      }
      try {
        b.parsed_data = b.details ? JSON.parse(b.details) : null;
      } catch (e) {
        b.parsed_data = null;
      }
      this.groupedBookmarks[type].push(b);
    });
    this.topics = Object.keys(this.groupedBookmarks);
  }

  deleteBookmark(id: number | undefined, event: Event) {
    event.stopPropagation();
    if (!id) return;
    this.bookmarkService.deleteBookmark(id).subscribe(() => {
      this.loadBookmarks();
    });
  }
}
