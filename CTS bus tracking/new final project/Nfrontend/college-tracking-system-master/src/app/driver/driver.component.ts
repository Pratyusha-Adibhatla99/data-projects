import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { UtilService } from '../util.service';

@Component({
  selector: 'app-driver',
  templateUrl: './driver.component.html',
  styleUrls: ['./driver.component.scss']
})
export class DriverComponent implements OnInit {
  isHome!: Boolean;

  constructor(
    private service: UtilService,
    private router: Router
  ) { }

  ngOnInit() {
    this.service.isHome.subscribe(res => {
      this.isHome = res;
    });
  }

  logout() {
    this.router.navigateByUrl('/driver/login');
  }
}
