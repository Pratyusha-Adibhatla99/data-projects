package com.springboot.h2;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.context.properties.EnableConfigurationProperties;

@EnableConfigurationProperties
@SpringBootApplication
public class Appmain {

	public static void main(String[] args) {
		SpringApplication.run(Appmain.class, args);
	}
}
