import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SpiritualComponent } from './spiritual.component';

describe('SpiritualComponent', () => {
  let component: SpiritualComponent;
  let fixture: ComponentFixture<SpiritualComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SpiritualComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(SpiritualComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
