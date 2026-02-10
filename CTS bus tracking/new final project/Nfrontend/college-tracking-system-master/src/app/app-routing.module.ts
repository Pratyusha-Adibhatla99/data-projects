import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { AdminBusrouteComponent } from './admin/admin-busroute/admin-busroute.component';
import { AdminHomeComponent } from './admin/admin-home/admin-home.component';
import { AdminLoginComponent } from './admin/admin-login/admin-login.component';
import { AdminTrackingComponent } from './admin/admin-tracking/admin-tracking.component';
import { AdminUsersComponent } from './admin/admin-users/admin-users.component';
import { AdminComponent } from './admin/admin.component';
import { DriverHomeComponent } from './driver/driver-home/driver-home.component';
import { DriverLoginComponent } from './driver/driver-login/driver-login.component';
import { DriverRouteComponent } from './driver/driver-route/driver-route.component';
import { DriverTrackingComponent } from './driver/driver-tracking/driver-tracking.component';
import { DriverComponent } from './driver/driver.component';
import { HomeComponent } from './home/home.component';
import { RegistrationComponent } from './registration/registration.component';
import { UserBusRouteComponent } from './user/user-bus-route/user-bus-route.component';
import { UserBusTrackingComponent } from './user/user-bus-tracking/user-bus-tracking.component';
import { UserHomeComponent } from './user/user-home/user-home.component';
import { UserLoginComponent } from './user/user-login/user-login.component';
import { UserProfileComponent } from './user/user-profile/user-profile.component';
import { UserComponent } from './user/user.component';

const routes: Routes = [
  { path: '', component: HomeComponent },
  { path: 'register', component: RegistrationComponent },
  { path: 'admin', component: AdminComponent, children: [
    { path: 'login', component: AdminLoginComponent },
    { path: 'home', component: AdminHomeComponent },
    { path: 'user', component: AdminUsersComponent },
    { path: 'bus-route', component: AdminBusrouteComponent },
    { path: 'bus-tracking', component: AdminTrackingComponent }
  ]},
  { path: 'driver', component: DriverComponent, children: [
    { path: 'login', component: DriverLoginComponent },
    { path: 'home', component: DriverHomeComponent },
    { path: 'route', component: DriverRouteComponent },
    { path: 'tracking', component: DriverTrackingComponent }
  ]},
  { path: 'user', component: UserComponent, children: [
    { path: 'login', component: UserLoginComponent },
    { path: 'home', component: UserHomeComponent },
    { path: 'profile', component: UserProfileComponent },
    { path: 'bus-route', component: UserBusRouteComponent },
    { path: 'bus-tracking', component: UserBusTrackingComponent }
  ]},
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
