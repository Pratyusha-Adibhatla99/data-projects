import { Component, OnInit } from '@angular/core';
import { FormGroup, FormControl, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { UtilService } from 'src/app/util.service';

@Component({
   selector: 'app-admin-login',
   templateUrl: './admin-login.component.html',
   styleUrls: ['./admin-login.component.scss']
})
export class AdminLoginComponent implements OnInit {
   formdata!: FormGroup;
   constructor(
      private service: UtilService,
      private router: Router
   ) { }

   ngOnInit() {
      this.service.isHome.next(true);
      this.formdata = new FormGroup({
         passwd: new FormControl("", Validators.required),
         userName: new FormControl("", Validators.required),
      });
   }

   login() {
      if (this.formdata.valid) {
         if (this.formdata.value.userName === 'admin' && this.formdata.value.passwd === 'admin') {
            alert("User logged in successfully !!!");
            this.service.isHome.next(false);
            this.router.navigateByUrl('/admin/home');
         } else {
            alert("Invalid credentails !!!");
         } 
      } else {
         alert("Enter credentails !!!");
      }
   }

}
