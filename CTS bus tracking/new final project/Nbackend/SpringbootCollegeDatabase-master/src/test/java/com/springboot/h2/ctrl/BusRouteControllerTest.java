package com.springboot.h2.ctrl;

import com.springboot.h2.model.BusRoute;
import com.springboot.h2.serv.BusService;
import com.springboot.h2.util.UtilTest;
import org.junit.Assert;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.MockitoJUnitRunner;

import java.util.List;

import static org.mockito.Mockito.when;

@RunWith(MockitoJUnitRunner.class)
public class BusRouteControllerTest {

    @Mock
    private BusService busService;

    @InjectMocks
    private BusController busController;

    @Test
    public void testGetAllBusRoutes() {
        List<BusRoute> busRoutes = UtilTest.getBusRouteList();
        when(busService.getBusRoutes()).thenReturn(busRoutes);
        List<BusRoute> resList = busController.getBusRoutes();
        Assert.assertEquals(busRoutes.size(), resList.size());
    }

    @Test
    public void testGetBusRouteById() {
        BusRoute busRoute = UtilTest.getBusRoute();
        when(busService.getBusRouteById(1)).thenReturn(busRoute);
        BusRoute res = busController.getBusRouteById(1);
        Assert.assertEquals(busRoute.getDriverName(), res.getDriverName());
    }

    @Test
    public void getBusRouteByIdAndDriver() {
        BusRoute busRoute = UtilTest.getBusRoute();
        when(busService.getBusRouteByIdAndDriver(1, "driver")).thenReturn(busRoute);
        BusRoute res = busController.getBusRouteByIdAndDriver(1, "driver");
        Assert.assertEquals(busRoute.getSource(), res.getSource());
    }

}
