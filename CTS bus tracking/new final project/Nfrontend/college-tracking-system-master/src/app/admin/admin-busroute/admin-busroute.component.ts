import { Component, OnInit } from '@angular/core';
import { FormGroup, FormControl, Validators } from '@angular/forms';
import { AppService } from 'src/app/app.service';
import { BusRoute } from 'src/app/BusRoute';

@Component({
  selector: 'app-admin-busroute',
  templateUrl: './admin-busroute.component.html',
  styleUrls: ['./admin-busroute.component.scss']
})
export class AdminBusrouteComponent implements OnInit {
  formdata!: FormGroup;
  constructor(private appService: AppService) { }

  ngOnInit() {
    this.formdata = new FormGroup({
      routeNo: new FormControl("", Validators.required),
      busNo: new FormControl("", Validators.required),
      driverName: new FormControl("", Validators.required),
      source: new FormControl("", Validators.required),
      sourceLat: new FormControl("", Validators.required),
      sourcelong: new FormControl("", Validators.required),
      destination: new FormControl("", Validators.required),
      destinationLat: new FormControl("", Validators.required),
      destinationlong: new FormControl("", Validators.required)
    });
  }

  addBusRoute() {
    if (this.formdata.valid) {
      const busroute = this.setBusRouteDetails(this.formdata.value);
      this.appService.savBusRoute(busroute).subscribe(res => {
        if (res > 0) {
          alert("Bus route added successfully !!!");
          this.formdata.reset();
        }
      });
    } else {
      alert("Complete all required fields !!!");
    }
  }

  setBusRouteDetails(formData: any) {
    let busroute = new BusRoute();
    busroute.routeNo = Number(formData.routeNo);
    busroute.driverName = formData.driverName;
    busroute.busNo = formData.busNo;
    busroute.source = formData.source;
    busroute.source_lat = formData.sourceLat;
    busroute.source_long = formData.sourcelong;
    busroute.destination = formData.destination;
    busroute.destination_lat = formData.destinationLat;
    busroute.destination_long = formData.destinationlong;
    return busroute;
  }

}
