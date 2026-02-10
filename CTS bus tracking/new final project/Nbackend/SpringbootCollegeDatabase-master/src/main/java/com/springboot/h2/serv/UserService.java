package com.springboot.h2.serv;

import com.springboot.h2.model.User;
import com.springboot.h2.repo.UserDaoRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.List;

@Service
public class UserService {

	@Autowired
	UserDaoRepository repository;

	public void save(final User user) {
		repository.save(user);
	}

	public List<User> getUser() {
		final List<User> users = new ArrayList<>();
		repository.findAll().forEach(user -> users.add(user));
		return users;
	}

	public User getUserById(int id) {
		return repository.findById(id).get();
	}

	public User userLogin(String userName, String password) {
		return repository.findByNameAndPassword(userName, password);
	}
}
