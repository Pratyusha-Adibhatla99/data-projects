import { Injectable } from '@angular/core';
 
import { HttpClient, HttpParams, HttpHeaders } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { map, catchError} from 'rxjs/operators';
import { User } from './User';
import { BusRoute } from './BusRoute';
 
@Injectable()
export class AppService {
 
  baseURL: string = "http://localhost:10090/";
 
  constructor(private http: HttpClient) {
  }
 
  getUsers(): Observable<any> {
    return this.http.get(this.baseURL + 'user');
  }

  getUserById(id: number): Observable<any> {
    return this.http.get(this.baseURL + 'user/' + id);
  }
 
  saveUser(user: User): Observable<any> {
    return this.http.post(this.baseURL + 'user', user);
  }

  updateUser(user: User): Observable<any> {
    return this.http.post(this.baseURL + 'user/update', user);
  }

  getBusRoutes(): Observable<any> {
    return this.http.get(this.baseURL + 'bus');
  }

  getBusRouteById(id: number): Observable<any> {
    return this.http.get(this.baseURL + 'bus/' + id);
  }

  getBusRouteByRouteId(id: number): Observable<any> {
    let params = new HttpParams();
    params = params.append('routeId', id);
    return this.http.get(this.baseURL + 'bus/get',  {params: params});
  }
 
  savBusRoute(user: BusRoute): Observable<any> {
    return this.http.post(this.baseURL + 'bus', user);
  }

  updateBusRoute(user: BusRoute): Observable<any> {
    return this.http.post(this.baseURL + 'bus/update/location', user);
  }

  getBusRouteByIdAndDriver(id: number, name: string): Observable<any> {
    let params = new HttpParams();
    params = params.append('id', id);
    params = params.append('name', name);

    return this.http.get(this.baseURL + 'bus/driver/login', {params: params});
  }

  userLogin(userName: string, password: string): Observable<any> {
    let params = new HttpParams();
    params = params.append('userName', userName);
    params = params.append('password', password);

    return this.http.get(this.baseURL + 'user/login', {params: params});
  }

}
 