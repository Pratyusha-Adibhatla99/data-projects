package com.springboot.h2.repo;

import com.springboot.h2.model.User;
import org.springframework.data.repository.CrudRepository;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

@Repository
public interface UserDaoRepository extends CrudRepository<User, Integer>{

    User findByNameAndPassword(@Param("userName") String userName, @Param("password") String password);
}
