package com.springboot.h2.ctrl;

import com.springboot.h2.model.BusRoute;
import com.springboot.h2.serv.BusService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import javax.validation.Valid;
import java.util.List;

@RestController
@RequestMapping("/bus")
public class BusController {

    private final Logger log = LoggerFactory.getLogger(this.getClass());

    @Autowired
    BusService service;

    @PostMapping
    public int saveBusRoute(final @RequestBody @Valid BusRoute busRoute) {
        log.info("Saving user details in the database.");
        busRoute.setCurrentLocation(busRoute.getSource());
        busRoute.setCurrentLocation_lat(busRoute.getSource_lat());
        busRoute.setCurrentLocation_long(busRoute.getSource_long());
        service.saveBusRoute(busRoute);
        return busRoute.getId();
        
    }
    @PostMapping(value = "/update/gps")
    public String updateGpsLocation(@RequestParam("routeId") int routeId,
                                    @RequestParam("lat") String lat,
                                    @RequestParam("lon") String lon) {
        
        log.info("Received High-Frequency GPS Update for Route: " + routeId);
        
        // Pass data to the Service layer for Validation & Normalization
        // (This calls the logic you added to BusService.java earlier)
        service.updateBusLocation(routeId, lat, lon);
        
        return "GPS Update Processed: Validation & Normalization Applied.";
    }

    @PostMapping(value = "/update/location")
    public BusRoute updateCurrentLocation(final @RequestBody @Valid BusRoute busRoute) {
        log.info("Update user details in the database.");
        service.saveBusRoute(busRoute);
        return busRoute;
    }

    @GetMapping
    public List<BusRoute> getBusRoutes() {
        log.info("Getting BusRoute details from the database.");
        return service.getBusRoutes();
    }

    @GetMapping(value= "/{id}")
    public BusRoute getBusRouteById(@PathVariable("id") int id) {
        log.info("Getting BusRoute details from the database.");
        return service.getBusRouteById(id);
    }

    @GetMapping(value= "/get")
    public BusRoute getBusRouteByRouteId(@RequestParam("routeId") int routeId) {
        log.info("Getting BusRoute details from the database.");
        return service.getBusRouteByRouteId(routeId);
    }

    @GetMapping(value= "/driver/login")
    public BusRoute getBusRouteByIdAndDriver(@RequestParam("id") int id, @RequestParam("name") String name) {
        log.info("Getting BusRoute details from the database.");
        return service.getBusRouteByIdAndDriver(id, name);
    }
}
