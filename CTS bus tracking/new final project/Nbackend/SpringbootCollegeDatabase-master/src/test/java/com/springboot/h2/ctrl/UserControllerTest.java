package com.springboot.h2.ctrl;

import com.springboot.h2.model.User;
import com.springboot.h2.serv.UserService;
import com.springboot.h2.util.UtilTest;
import org.junit.Assert;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.MockitoJUnitRunner;

import java.text.ParseException;
import java.util.List;

import static org.mockito.Mockito.when;

@RunWith(MockitoJUnitRunner.class)
public class UserControllerTest {

    @Mock
    private UserService userService;

    @InjectMocks
    private UserController userController;

    @Test
    public void testGetAllUsers() throws ParseException {
        List<User> users = UtilTest.getUserList();
        when(userService.getUser()).thenReturn(users);
        List<User> resList = userController.getUsers();
        Assert.assertEquals(users.size(), resList.size());
    }

    @Test
    public void testGetUser() throws ParseException {
        User user = UtilTest.getUser();
        when(userService.getUserById(1)).thenReturn(user);
        User res = userController.getUserById(1);
        Assert.assertEquals(user.getName(), res.getName());
    }

    @Test
    public void testUserLogin() throws ParseException {
        User user = UtilTest.getUser();
        when(userService.userLogin("test@gmail.com", "test")).thenReturn(user);
        User res = userController.userLogin("test@gmail.com", "test");
        Assert.assertEquals(user.getName(), res.getName());
    }

}
