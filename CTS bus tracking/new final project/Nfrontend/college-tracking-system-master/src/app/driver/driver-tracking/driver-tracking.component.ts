import { Component, OnInit } from '@angular/core';
import { FormGroup, FormControl, Validators } from '@angular/forms';
import { AppService } from 'src/app/app.service';
import { BusRoute } from 'src/app/BusRoute';
import { User } from 'src/app/User';
import { UtilService } from 'src/app/util.service';

@Component({
  selector: 'app-driver-tracking',
  templateUrl: './driver-tracking.component.html',
  styleUrls: ['./driver-tracking.component.scss']
})
export class DriverTrackingComponent implements OnInit {
  formdata!: FormGroup;
  busRoute!: BusRoute;
  constructor(private appService: AppService,
    private service: UtilService) { }

  ngOnInit() {
    this.busRoute = this.service.busRoute.value;
    this.formdata = new FormGroup({
      routeNo: new FormControl("", Validators.required),
      source: new FormControl("", Validators.required),
      sourceLat: new FormControl("", Validators.required),
      sourcelong: new FormControl("", Validators.required)
    });
  }

  addBusRoute() {
    if (this.formdata.valid) {
      this.setLocationDetails(this.formdata.value);
      this.appService.updateBusRoute(this.busRoute).subscribe(res => {
        if (res) {
          this.service.busRoute.next(res);
          alert("Tracking Details added successfully !!!");
        } else {
          alert("Update failed !!!");
        }
      });
    } else {
      alert("Complete all required fields !!!");
    }
  }

  setLocationDetails(formData: any) {
    this.busRoute.currentLocation = formData.source;
    this.busRoute.currentLocation_lat = formData.sourceLat;
    this.busRoute.currentLocation_long = formData.sourcelong;
  }
}
