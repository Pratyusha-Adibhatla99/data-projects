import { ComponentFixture, TestBed } from '@angular/core/testing';

import { UserBusTrackingComponent } from './user-bus-tracking.component';

describe('UserBusTrackingComponent', () => {
  let component: UserBusTrackingComponent;
  let fixture: ComponentFixture<UserBusTrackingComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ UserBusTrackingComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(UserBusTrackingComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
