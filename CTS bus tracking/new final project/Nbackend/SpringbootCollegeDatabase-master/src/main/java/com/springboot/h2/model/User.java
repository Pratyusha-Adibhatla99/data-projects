package com.springboot.h2.model;

import com.fasterxml.jackson.annotation.JsonFormat;
import com.fasterxml.jackson.annotation.JsonIgnore;

import javax.persistence.Entity;
import javax.persistence.GeneratedValue;
import javax.persistence.GenerationType;
import javax.persistence.Id;
import java.util.Date;

@Entity
public class User {

	@Id
	 @GeneratedValue(strategy = GenerationType.IDENTITY)
	private int id;
	private String name;
	private String emailAddress;
	private String password;
	private String gender;
	private String address;
	private String mobileNumber;
	@JsonFormat(pattern = "yyyy-mm-dd")
	private Date dob;
	private boolean isActive;

	public User() {
	}

	public User(int id, String name, String emailAddress, String password, String gender, String address, String mobileNumber, Date dob, boolean isActive) {
		this.id = id;
		this.name = name;
		this.emailAddress = emailAddress;
		this.password = password;
		this.gender = gender;
		this.address = address;
		this.mobileNumber = mobileNumber;
		this.dob = dob;
		this.isActive = isActive;
	}

	public int getId() {
		return id;
	}

	public void setId(int id) {
		this.id = id;
	}

	public String getName() {
		return name;
	}

	public void setName(String name) {
		this.name = name;
	}

	public String getEmailAddress() {
		return emailAddress;
	}

	public void setEmailAddress(String emailAddress) {
		this.emailAddress = emailAddress;
	}

	public String getPassword() {
		return password;
	}

	public void setPassword(String password) {
		this.password = password;
	}

	public String getGender() {
		return gender;
	}

	public void setGender(String gender) {
		this.gender = gender;
	}

	public String getAddress() {
		return address;
	}

	public void setAddress(String address) {
		this.address = address;
	}

	public String getMobileNumber() {
		return mobileNumber;
	}

	public void setMobileNumber(String mobileNumber) {
		this.mobileNumber = mobileNumber;
	}

	public Date getDob() {
		return dob;
	}

	public void setDob(Date dob) {
		this.dob = dob;
	}

	public boolean isActive() {
		return isActive;
	}

	public void setActive(boolean active) {
		isActive = active;
	}
}
