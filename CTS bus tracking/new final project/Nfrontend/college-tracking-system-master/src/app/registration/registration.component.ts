import { Component, OnInit } from '@angular/core';
import { FormGroup, FormControl, Validators } from '@angular/forms';
import { AppService } from '../app.service';
import { User } from '../User';

@Component({
   selector: 'app-registration',
   templateUrl: './registration.component.html',
   styleUrls: ['./registration.component.scss']
})
export class RegistrationComponent implements OnInit {
   todaydate: any;
   componentproperty: any;
   emailid: any;
   formdata!: FormGroup;
   genderList: any[] = [
      { value: 'male', viewValue: 'Male' },
      { value: 'female', viewValue: 'Female' }
   ];

   constructor(private appService: AppService) { }

   ngOnInit() {
      this.formdata = new FormGroup({
         emailid: new FormControl("", Validators.compose([
            Validators.required,
            Validators.pattern("[^ @]*@[^ @]*")
         ])),
         passwd: new FormControl("", Validators.required),
         name: new FormControl("", Validators.required),
         mobileNum: new FormControl("", Validators.required),
         gender: new FormControl("", Validators.required),
         address: new FormControl("", Validators.required),
         dob: new FormControl("", Validators.required)
      });
   }

   submit() {
      if (this.formdata.valid) {
         const user = this.setUserDetails(this.formdata.value);
         this.appService.saveUser(user).subscribe(res => {
            if (res > 0) {
               alert("User registered successfully !!!");
               this.formdata.reset();
            }
         });
      } else {
         alert("Fill out all the required fields !!!");
      }
   }

   setUserDetails(formData: any) {
      let user = new User();
      user.name = formData.name;
      user.emailAddress = formData.emailid;
      user.gender = formData.gender;
      user.dob = formData.dob;
      user.mobileNumber = formData.mobileNum;
      user.password = formData.passwd;
      user.address = formData.address;
      return user;
   }
}
