package com.springboot.h2.repo;

import com.springboot.h2.model.BusRoute;
import org.springframework.data.repository.CrudRepository;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

@Repository
public interface BusDaoRepository extends CrudRepository<BusRoute, Integer>{

    BusRoute findByRouteNoAndDriverName(@Param("id") int id, @Param("name") String name);

    BusRoute findByRouteNo(@Param("id") int id);
}
