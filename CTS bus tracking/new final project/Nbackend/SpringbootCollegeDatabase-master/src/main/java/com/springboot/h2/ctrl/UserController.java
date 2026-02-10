package com.springboot.h2.ctrl;

import com.springboot.h2.model.BusRoute;
import com.springboot.h2.model.User;
import com.springboot.h2.serv.UserService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import javax.validation.Valid;
import java.util.List;

@RestController
@RequestMapping("/user")
public class UserController {

	private final Logger log = LoggerFactory.getLogger(this.getClass()); 

	@Autowired
	UserService service;

	@PostMapping
	public int saveUser(final @RequestBody @Valid User user) {
		log.info("Saving user details in the database.");
		user.setActive(false);
		service.save(user);
		return user.getId();
	}

	@PostMapping(value= "/update")
	public User updateUser(final @RequestBody @Valid User user) {
		log.info("Update user details in the database.");
		service.save(user);
		return user;
	}

	@GetMapping
	public List<User> getUsers() {
		log.info("Getting student details from the database.");
		return service.getUser();
	}

	@GetMapping(value= "/{id}")
	public User getUserById(@PathVariable("id") int id) {
		log.info("Getting student details from the database.");
		return service.getUserById(id);
	}

	@GetMapping(value= "/login")
	public User userLogin(@RequestParam("userName") String userName, @RequestParam("password") String password) {
		log.info("Getting User details from the database.");
		return service.userLogin(userName, password);
	}
}
