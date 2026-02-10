package com.springboot.h2.util;

import com.springboot.h2.model.BusRoute;
import com.springboot.h2.model.User;

import java.text.DateFormat;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.List;

public final class UtilTest {

    public static final User getUser() throws ParseException {
        User user = new User();
        user.setName("test_name");
        user.setEmailAddress("test@gmail.com");
        user.setPassword("password");
        user.setGender("male");
        user.setAddress("test_address");
        user.setMobileNumber("123456789");
        user.setActive(false);
        DateFormat formatter = new SimpleDateFormat("yyyy-mm-dd");
        user.setDob(formatter.parse("2021-06-12"));
        return user;
    }

    public static final List<User> getUserList() throws ParseException {
        final List<User> users = new ArrayList<>();
        users.add(getUser());
        users.add(getUser());
        users.add(getUser());
        return users;
    }

    public static final BusRoute getBusRoute() {
        BusRoute busRoute = new BusRoute();
        busRoute.setBusNo("test_bus_no");
        busRoute.setRouteNo(5);
        busRoute.setDriverName("test_driver");
        busRoute.setSource("test_source");
        busRoute.setSource_lat("test_source_lat");
        busRoute.setSource_long("set_source_long");
        busRoute.setCurrentLocation("test_current");
        busRoute.setCurrentLocation_lat("test_current_lat");
        busRoute.setCurrentLocation_long("set_current_long");
        busRoute.setDestination("test_destination");
        busRoute.setDestination_lat("test_destination_lat");
        busRoute.setDestination_long("set_destination_long");
        return busRoute;
    }

    public static final List<BusRoute> getBusRouteList() {
        final List<BusRoute> busRoutes = new ArrayList<>();
        busRoutes.add(getBusRoute());
        busRoutes.add(getBusRoute());
        busRoutes.add(getBusRoute());
        return busRoutes;
    }

}
