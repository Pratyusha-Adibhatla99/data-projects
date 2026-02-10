import { Component, OnInit } from '@angular/core';
import { FormGroup, FormControl, Validators } from '@angular/forms';
import { AppService } from 'src/app/app.service';
import { BusRoute } from 'src/app/BusRoute';
import { UtilService } from 'src/app/util.service';

@Component({
  selector: 'app-admin-tracking',
  templateUrl: './admin-tracking.component.html',
  styleUrls: ['./admin-tracking.component.scss']
})
export class AdminTrackingComponent implements OnInit {
  formdata!: FormGroup;
  busRoute!: BusRoute;
  isTracking: boolean = false;
  routeNumberList!: any[];
  constructor(private service: UtilService,
    private appService: AppService) { }

  ngOnInit(): void {
    this.setBusRoutes();
    this.formdata = new FormGroup({
      routeNumber: new FormControl("", Validators.required),
    });
  }

  track() {
    if (this.formdata.valid) {
      this.appService.getBusRouteByRouteId(this.formdata.value.routeNumber).subscribe(res => {
        if (res) {
          this.isTracking = true;
          this.busRoute = res;
        } else {
          alert("Invalid Bus Route !!!");
        }
      });
    } else {
      alert("Select Bus Route !!!");
    }
  }

  setBusRoutes() {
    this.appService.getBusRoutes().subscribe(res => {
      if(res.length > 0) {
        this.routeNumberList = res.map((r: { routeNo: any; }) => r.routeNo);
      }
    })
  }

}
