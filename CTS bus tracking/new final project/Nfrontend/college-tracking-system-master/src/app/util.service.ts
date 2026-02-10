import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';
import { BusRoute } from './BusRoute';

@Injectable({
  providedIn: 'root',
})
export class UtilService {
  isHome = new BehaviorSubject<Boolean>(true);
  busRoute = new BehaviorSubject<any>(null);
  user = new BehaviorSubject<any>(null);
}