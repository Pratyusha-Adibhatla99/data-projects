import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AdminBusrouteComponent } from './admin-busroute.component';

describe('AdminBusrouteComponent', () => {
  let component: AdminBusrouteComponent;
  let fixture: ComponentFixture<AdminBusrouteComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ AdminBusrouteComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(AdminBusrouteComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
