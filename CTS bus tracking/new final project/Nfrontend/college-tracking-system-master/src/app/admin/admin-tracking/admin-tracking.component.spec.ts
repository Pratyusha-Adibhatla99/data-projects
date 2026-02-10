import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AdminTrackingComponent } from './admin-tracking.component';

describe('AdminTrackingComponent', () => {
  let component: AdminTrackingComponent;
  let fixture: ComponentFixture<AdminTrackingComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ AdminTrackingComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(AdminTrackingComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
