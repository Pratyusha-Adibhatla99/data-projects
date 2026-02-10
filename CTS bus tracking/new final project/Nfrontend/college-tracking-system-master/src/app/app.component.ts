import { Component } from '@angular/core';
import { ActivatedRoute, ActivatedRouteSnapshot, Router } from '@angular/router';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent {
  title = 'college-tracking-system';
  isHome = false;
  isAdmin = false;
  isDriver = false;
  isUser = false;

  constructor(private router: Router,
    private route: ActivatedRoute) { }

  ngOnInit(): void {
    this.setHeaderButtons();
  }

  setHeaderButtons() {
    const url = this.router.url;
    const u = this.route.url;
    this.isHome = true;
    if (url.includes('/admin') && !url.includes('/admin/login')) {
      this.isAdmin = true;
      this.isHome = false;
    }
    if (url.includes('/user') && !url.includes('/user/login')) {
      this.isUser = true;
      this.isHome = false;
    }
    if (url.includes('/driver') && !url.includes('/driver/login')) {
      this.isDriver = true;
      this.isHome = false;
    }
  }
}
