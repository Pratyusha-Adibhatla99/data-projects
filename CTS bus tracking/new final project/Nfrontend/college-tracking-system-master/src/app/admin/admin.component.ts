import { Component, OnInit } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { UtilService } from '../util.service';

@Component({
  selector: 'app-admin',
  templateUrl: './admin.component.html',
  styleUrls: ['./admin.component.scss']
})
export class AdminComponent implements OnInit {
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
    this.router.navigateByUrl('/admin/login');
  }

}
