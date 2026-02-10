import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { UtilService } from '../util.service';

@Component({
  selector: 'app-user',
  templateUrl: './user.component.html',
  styleUrls: ['./user.component.scss']
})
export class UserComponent implements OnInit {
  isHome!: Boolean;
  constructor(private service: UtilService,
    private router: Router) { }

  ngOnInit(): void {
    this.service.isHome.subscribe(res => {
      this.isHome = res;
    });
  }

  logout() {
    this.router.navigateByUrl('/user/login');
  }

}
