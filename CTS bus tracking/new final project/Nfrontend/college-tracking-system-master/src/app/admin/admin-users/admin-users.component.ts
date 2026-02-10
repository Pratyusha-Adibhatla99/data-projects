import { Component, OnInit } from '@angular/core';
import { AppService } from 'src/app/app.service';
import { User } from 'src/app/User';

@Component({
  selector: 'app-admin-users',
  templateUrl: './admin-users.component.html',
  styleUrls: ['./admin-users.component.scss']
})
export class AdminUsersComponent implements OnInit {
  userList: any[] = [];
  constructor(private appService: AppService) { }

  ngOnInit(): void {
    this.appService.getUsers().subscribe(res => {
      this.userList = res;
    });
  }

  setUserActivate(user: any, isActivate: boolean) {
    user.active = isActivate;
    this.appService.updateUser(user).subscribe(res => {
      user = res;
    });
  }



}
