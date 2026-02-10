package com.springboot.h2.serv;

import com.springboot.h2.model.BusRoute;
import com.springboot.h2.repo.BusDaoRepository;
import com.springboot.h2.util.UtilTest;
import org.junit.Assert;
import org.junit.Before;
import org.junit.Test;
import org.junit.jupiter.api.DisplayName;
import org.junit.runner.RunWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;
import org.springframework.test.context.junit4.SpringJUnit4ClassRunner;

import java.util.List;

import static org.mockito.Mockito.when;

@RunWith(SpringJUnit4ClassRunner.class)
public class BusRouteServiceTest {

    @Mock
    private BusDaoRepository busRepository;

    @InjectMocks
    private BusService busService;

    @Before
    public void setup() {
        MockitoAnnotations.initMocks(this);
    }

    @Test
    @DisplayName("test get all bus routes")
    public void testGetAllBusRoutes() {
        List<BusRoute> busRouteList = UtilTest.getBusRouteList();
        when(busRepository.findAll()).thenReturn(busRouteList);
        List<BusRoute> busRoutesResponse = busService.getBusRoutes();

        Assert.assertEquals(busRouteList.size(), busRoutesResponse.size());
        Assert.assertEquals(busRouteList.get(0).getBusNo(), busRoutesResponse.get(0).getBusNo());
    }

    @Test
    @DisplayName("test get bus route by bus route no and driver name")
    public void testGetBusRouteByIdAndDriver() {
        BusRoute busRoute = UtilTest.getBusRoute();
        when(busRepository.findByRouteNoAndDriverName(2, "driver")).thenReturn(busRoute);
        BusRoute busRouteResponse = busService.getBusRouteByIdAndDriver(2, "driver");

        Assert.assertEquals(busRoute.getSource(), busRouteResponse.getSource());
        Assert.assertEquals(busRoute.getDestination(), busRouteResponse.getDestination());
    }
}
