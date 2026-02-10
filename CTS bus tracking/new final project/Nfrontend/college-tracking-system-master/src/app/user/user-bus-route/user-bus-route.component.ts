import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { AppService } from 'src/app/app.service';
import { BusRoute } from 'src/app/BusRoute';
import { UtilService } from 'src/app/util.service';

@Component({
  selector: 'app-user-bus-route',
  templateUrl: './user-bus-route.component.html',
  styleUrls: ['./user-bus-route.component.scss']
})
export class UserBusRouteComponent implements OnInit {
  busRoutes: BusRoute[] = [];
  constructor(
    private service: UtilService,
    private router: Router,
    private appService: AppService
 ) { }

  ngOnInit(): void {
    this.appService.getBusRoutes().subscribe(res => {
      if (res && res.length > 0) {
        this.busRoutes = res;
      }
    });
  }

}
