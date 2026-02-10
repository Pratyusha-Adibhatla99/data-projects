import { Component, OnInit } from '@angular/core';
import { User } from 'src/app/User';
import { UtilService } from 'src/app/util.service';

@Component({
  selector: 'app-user-home',
  templateUrl: './user-home.component.html',
  styleUrls: ['./user-home.component.scss']
})
export class UserHomeComponent implements OnInit {
  user!: User;

  constructor(private service: UtilService) { }

  ngOnInit(): void {
    this.user = this.service.user.value;
  }

}
