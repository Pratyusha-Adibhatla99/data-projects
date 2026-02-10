import { ComponentFixture, TestBed } from '@angular/core/testing';

import { UserBusRouteComponent } from './user-bus-route.component';

describe('UserBusRouteComponent', () => {
  let component: UserBusRouteComponent;
  let fixture: ComponentFixture<UserBusRouteComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ UserBusRouteComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(UserBusRouteComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
