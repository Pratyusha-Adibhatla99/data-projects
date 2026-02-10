import { Component, OnInit } from '@angular/core';
import { AppService } from 'src/app/app.service';
import { UtilService } from 'src/app/util.service';

@Component({
  selector: 'app-driver-route',
  templateUrl: './driver-route.component.html',
  styleUrls: ['./driver-route.component.scss']
})
export class DriverRouteComponent implements OnInit {
  busRoute!: any;
  constructor(
    private service: UtilService,
    private appService: AppService
 ) { }

  ngOnInit(): void {
    this.service.isHome.next(false);
    this.busRoute = this.service.busRoute.value;
  }

}
