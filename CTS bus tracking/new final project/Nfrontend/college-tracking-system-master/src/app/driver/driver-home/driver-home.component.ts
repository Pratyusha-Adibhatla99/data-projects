import { Component, OnInit } from '@angular/core';
import { AppService } from 'src/app/app.service';
import { UtilService } from 'src/app/util.service';

@Component({
  selector: 'app-driver-home',
  templateUrl: './driver-home.component.html',
  styleUrls: ['./driver-home.component.scss']
})
export class DriverHomeComponent implements OnInit {
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
