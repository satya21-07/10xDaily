import { Component, Inject } from '@angular/core';
import { CommonModule, DatePipe } from '@angular/common';
import { MatButtonModule } from '@angular/material/button';
import { MatDialogModule, MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { MatIconModule } from '@angular/material/icon';
import { MatDividerModule } from '@angular/material/divider';
import { User } from '../../users.component';

@Component({
  selector: 'app-user-details-dialog',
  standalone: true,
  imports: [CommonModule, MatButtonModule, MatDialogModule, MatIconModule, MatDividerModule, DatePipe],
  templateUrl: './user-details-dialog.component.html',
  styleUrls: ['./user-details-dialog.component.scss']
})
export class UserDetailsDialogComponent {
  constructor(
    public dialogRef: MatDialogRef<UserDetailsDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public user: User
  ) {}

  close(): void {
    this.dialogRef.close();
  }

  formatTime(seconds: number): string {
    if (!seconds) return '0 mins';
    const mins = Math.floor(seconds / 60);
    const hrs = Math.floor(mins / 60);
    if (hrs > 0) {
      return `${hrs}h ${mins % 60}m`;
    }
    return `${mins} mins`;
  }
}
