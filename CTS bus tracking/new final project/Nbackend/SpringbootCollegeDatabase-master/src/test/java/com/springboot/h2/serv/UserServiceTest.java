package com.springboot.h2.serv;

import com.springboot.h2.model.User;
import com.springboot.h2.repo.UserDaoRepository;
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

import java.text.ParseException;
import java.util.List;

import static org.mockito.Mockito.when;

@RunWith(SpringJUnit4ClassRunner.class)
public class UserServiceTest {

    @Mock
    private UserDaoRepository userRepository;

    @InjectMocks
    private UserService userService;

    @Before
    public void setup() {
        MockitoAnnotations.initMocks(this);
    }

    @Test
    @DisplayName("test get all users")
    public void testGetAllUsers() throws ParseException {
        List<User> users = UtilTest.getUserList();
        when(userRepository.findAll()).thenReturn(users);
        List<User> usersResponse = userService.getUser();

        Assert.assertEquals(users.size(), usersResponse.size());
        Assert.assertEquals(users.get(0).getEmailAddress(), usersResponse.get(0).getEmailAddress());
    }

    @Test
    @DisplayName("test user login")
    public void testUserLogin() throws ParseException {
        User user = UtilTest.getUser();
        when(userRepository.findByNameAndPassword("test@gmail.com", "test")).thenReturn(user);
        User usersResponse = userService.userLogin("test@gmail.com", "test");

        Assert.assertEquals(user.getName(), usersResponse.getName());
    }
}
