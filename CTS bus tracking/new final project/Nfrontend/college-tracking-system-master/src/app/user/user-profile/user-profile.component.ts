import { Component, OnInit } from '@angular/core';
import { FormGroup, FormControl, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { AppService } from 'src/app/app.service';
import { User } from 'src/app/User';
import { UtilService } from 'src/app/util.service';

@Component({
  selector: 'app-user-profile',
  templateUrl: './user-profile.component.html',
  styleUrls: ['./user-profile.component.scss']
})
export class UserProfileComponent implements OnInit {
  formdata!: FormGroup;
  user!: User;
  genderList: any[] = [
   {value: 'male', viewValue: 'Male'},
   {value: 'female', viewValue: 'Female'}
 ];
 
 constructor(
   private service: UtilService,
   private router: Router,
   private appService: AppService
) { }
  
 ngOnInit() {
    this.user = this.service.user.value;
    this.formdata = new FormGroup({
       emailid: new FormControl("", Validators.compose([
          Validators.required,
          Validators.pattern("[^ @]*@[^ @]*")
       ])),
       name: new FormControl("", Validators.required),
       mobileNum: new FormControl("", Validators.required),
       gender: new FormControl("", Validators.required),
       address: new FormControl("", Validators.required),
    });
    this.setUserDetails(this.user);
 }

 setUserDetails(user: User) {
   this.formdata.patchValue({
      emailid: user.emailAddress,
      name: user.name,
      mobileNum: user.mobileNumber,
      gender: user.gender,
      address: user.address
    });
 }

}
