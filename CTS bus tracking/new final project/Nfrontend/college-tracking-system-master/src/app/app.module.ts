import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { CUSTOM_ELEMENTS_SCHEMA } from '@angular/core';
import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { RegistrationComponent } from './registration/registration.component';
import { HomeComponent } from './home/home.component';
import { ReactiveFormsModule } from '@angular/forms';
import { AdminComponent } from './admin/admin.component';
import { AdminHomeComponent } from './admin/admin-home/admin-home.component';
import { AdminLoginComponent } from './admin/admin-login/admin-login.component';
import { UtilService } from './util.service';
import { AdminUsersComponent } from './admin/admin-users/admin-users.component';
import { AdminBusrouteComponent } from './admin/admin-busroute/admin-busroute.component';
import { DriverComponent } from './driver/driver.component';
import { DriverHomeComponent } from './driver/driver-home/driver-home.component';
import { DriverLoginComponent } from './driver/driver-login/driver-login.component';
import { DriverRouteComponent } from './driver/driver-route/driver-route.component';
import { DriverTrackingComponent } from './driver/driver-tracking/driver-tracking.component';
import { UserComponent } from './user/user.component';
import { UserLoginComponent } from './user/user-login/user-login.component';
import { UserHomeComponent } from './user/user-home/user-home.component';
import { UserProfileComponent } from './user/user-profile/user-profile.component';
import { UserBusRouteComponent } from './user/user-bus-route/user-bus-route.component';
import { UserBusTrackingComponent } from './user/user-bus-tracking/user-bus-tracking.component';
import { AppService } from './app.service';
import { HttpClientModule } from '@angular/common/http';
import { AdminTrackingComponent } from './admin/admin-tracking/admin-tracking.component';

@NgModule({
  declarations: [
    AppComponent,
    RegistrationComponent,
    HomeComponent,
    AdminComponent,
    AdminHomeComponent,
    AdminLoginComponent,
    AdminUsersComponent,
    AdminBusrouteComponent,
    DriverComponent,
    DriverHomeComponent,
    DriverLoginComponent,
    DriverRouteComponent,
    DriverTrackingComponent,
    UserComponent,
    UserLoginComponent,
    UserHomeComponent,
    UserProfileComponent,
    UserBusRouteComponent,
    UserBusTrackingComponent,
    AdminTrackingComponent
  ],
  imports: [
    BrowserModule,
    BrowserAnimationsModule,
    AppRoutingModule,
    ReactiveFormsModule,
    HttpClientModule
  ],
  providers: [UtilService, AppService],
  schemas: [CUSTOM_ELEMENTS_SCHEMA],
  bootstrap: [AppComponent]
})
export class AppModule { }
