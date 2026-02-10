import { Component, OnInit } from '@angular/core';
import { FormGroup, FormControl, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { AppService } from 'src/app/app.service';
import { UtilService } from 'src/app/util.service';

@Component({
   selector: 'app-user-login',
   templateUrl: './user-login.component.html',
   styleUrls: ['./user-login.component.scss']
})
export class UserLoginComponent implements OnInit {
   formdata!: FormGroup;
   constructor(
      private service: UtilService,
      private router: Router,
      private appService: AppService
   ) { }

   ngOnInit() {
      this.service.isHome.next(true);
      this.formdata = new FormGroup({
         userName: new FormControl("", Validators.required),
         passwd: new FormControl("", Validators.required),
      });
   }

   login() {
      if (this.formdata.valid) {
         this.appService.userLogin(this.formdata.value.userName, this.formdata.value.passwd)
            .subscribe(res => {
               if (res) {
                  alert("User logged in successfully !!!");
                  this.service.isHome.next(false);
                  this.service.user.next(res);
                  this.router.navigateByUrl('/user/home');
               } else {
                  alert("Invalid credentails !!!");
               }
            });
      } else {
         alert("Enter credentails !!!");
      }
   }

}
