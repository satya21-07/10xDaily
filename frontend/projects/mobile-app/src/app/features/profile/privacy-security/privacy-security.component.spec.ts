import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PrivacySecurityComponent } from './privacy-security.component';

describe('PrivacySecurityComponent', () => {
  let component: PrivacySecurityComponent;
  let fixture: ComponentFixture<PrivacySecurityComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [PrivacySecurityComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(PrivacySecurityComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
