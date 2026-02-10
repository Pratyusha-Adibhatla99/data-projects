package com.springboot.h2.model;

import javax.persistence.Entity;
import javax.persistence.GeneratedValue;
import javax.persistence.GenerationType;
import javax.persistence.Id;

@Entity
public class BusRoute {

	@Id
	 @GeneratedValue(strategy = GenerationType.IDENTITY)
	private int id;
	private int routeNo;
	private String busNo;
	private String driverName;
	private String source;
	private String source_lat;
	private String source_long;
	private String destination;
	private String destination_lat;
	private String destination_long;
	private String currentLocation;
	private String currentLocation_lat;
	private String currentLocation_long;

	public BusRoute() {
	}

	public BusRoute(int id, int routeNo, String busNo, String driverName, String source, String source_lat, String source_long, String destination, String destination_lat, String destination_long, String currentLocation, String currentLocation_lat, String currentLocation_long) {
		this.id = id;
		this.routeNo = routeNo;
		this.busNo = busNo;
		this.driverName = driverName;
		this.source = source;
		this.source_lat = source_lat;
		this.source_long = source_long;
		this.destination = destination;
		this.destination_lat = destination_lat;
		this.destination_long = destination_long;
		this.currentLocation = currentLocation;
		this.currentLocation_lat = currentLocation_lat;
		this.currentLocation_long = currentLocation_long;
	}

	public int getId() {
		return id;
	}

	public void setId(int id) {
		this.id = id;
	}

	public int getRouteNo() {
		return routeNo;
	}

	public void setRouteNo(int routeNo) {
		this.routeNo = routeNo;
	}

	public String getBusNo() {
		return busNo;
	}

	public void setBusNo(String busNo) {
		this.busNo = busNo;
	}

	public String getDriverName() {
		return driverName;
	}

	public void setDriverName(String driverName) {
		this.driverName = driverName;
	}

	public String getSource() {
		return source;
	}

	public void setSource(String source) {
		this.source = source;
	}

	public String getSource_lat() {
		return source_lat;
	}

	public void setSource_lat(String source_lat) {
		this.source_lat = source_lat;
	}

	public String getSource_long() {
		return source_long;
	}

	public void setSource_long(String source_long) {
		this.source_long = source_long;
	}

	public String getDestination() {
		return destination;
	}

	public void setDestination(String destination) {
		this.destination = destination;
	}

	public String getDestination_lat() {
		return destination_lat;
	}

	public void setDestination_lat(String destination_lat) {
		this.destination_lat = destination_lat;
	}

	public String getDestination_long() {
		return destination_long;
	}

	public void setDestination_long(String destination_long) {
		this.destination_long = destination_long;
	}

	public String getCurrentLocation() {
		return currentLocation;
	}

	public void setCurrentLocation(String currentLocation) {
		this.currentLocation = currentLocation;
	}

	public String getCurrentLocation_lat() {
		return currentLocation_lat;
	}

	public void setCurrentLocation_lat(String currentLocation_lat) {
		this.currentLocation_lat = currentLocation_lat;
	}

	public String getCurrentLocation_long() {
		return currentLocation_long;
	}

	public void setCurrentLocation_long(String currentLocation_long) {
		this.currentLocation_long = currentLocation_long;
	}
}
