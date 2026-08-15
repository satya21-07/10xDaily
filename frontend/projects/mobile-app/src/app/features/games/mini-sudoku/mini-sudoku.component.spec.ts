import { ComponentFixture, TestBed } from '@angular/core/testing';

import { MiniSudokuComponent } from './mini-sudoku.component';

describe('MiniSudokuComponent', () => {
  let component: MiniSudokuComponent;
  let fixture: ComponentFixture<MiniSudokuComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [MiniSudokuComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(MiniSudokuComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
