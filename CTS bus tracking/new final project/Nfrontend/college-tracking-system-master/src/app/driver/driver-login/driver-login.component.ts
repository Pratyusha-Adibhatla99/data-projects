import { Component, OnInit } from '@angular/core';
import { FormGroup, FormControl, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { AppService } from 'src/app/app.service';
import { UtilService } from 'src/app/util.service';

@Component({
   selector: 'app-driver-login',
   templateUrl: './driver-login.component.html',
   styleUrls: ['./driver-login.component.scss']
})
export class DriverLoginComponent implements OnInit {
   formdata!: FormGroup;
   routeNumberList!: any[];
   constructor(
      private service: UtilService,
      private router: Router,
      private appService: AppService
   ) { }

   ngOnInit() {
      this.service.isHome.next(true);
      this.setBusRoutes();
      this.formdata = new FormGroup({
         driverName: new FormControl("", Validators.required),
         routeNumber: new FormControl("", Validators.required),
      });
   }

   login() {
      if (this.formdata.valid) {
         this.appService.getBusRouteByIdAndDriver(this.formdata.value.routeNumber, this.formdata.value.driverName)
            .subscribe(res => {
               if (res) {
                  alert("Driver logged in successfully !!!");
                  this.service.isHome.next(false);
                  this.service.busRoute.next(res);
                  this.router.navigateByUrl('/driver/home');
               } else {
                  alert("Invalid credentails !!!");
               }
            });
      } else {
         alert("Enter credentails !!!");
      }
   }

   setBusRoutes() {
      this.appService.getBusRoutes().subscribe(res => {
         if (res.length > 0) {
            this.routeNumberList = res.map((r: { routeNo: any; }) => r.routeNo);
         }
      })
   }

}
