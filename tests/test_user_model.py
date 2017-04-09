# -*- coding: utf-8 -*-
"""
Created on Tue Jan  3 15:35:45 2017

@author: leo
"""
import unittest
import time
from datetime import datetime
from app import create_app, db
from app.models import User, AnonymousUser, Role, Permission

class UserModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()
    #tearDown函数在测试后自动执行   
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()    
    
    def test_password_setter(self):
        u = User(password = 'cat')
        self.assertTrue(u.user_pwd_hash is not None)
        
    def test_no_password_getter(self):
        u = User(password = '123')
        with self.assertRaises(AttributeError):
            u.password
            
    def test_password_verification(self):
        u = User(password = '123')
        self.assertTrue(u.verify_password('123'))
        self.assertFalse(u.verify_password('456'))
        
    def test_password_salts_are_random(self):
        u1 = User(password = '123')
        u2 = User(password = '123')
        self.assertTrue(u1.user_pwd_hash != u2.user_pwd_hash)
    
    def test_roles_and_permissions(self):
        Role.insert_roles()
        u = User(user_name = 'leo',user_email='hhhparty@163.com', password='cat')
        self.assertTrue(u.can(Permission.WRITE_ARTICLES))
        self.assertTrue(u.can(Permission.MODERATE_COMMENTS))
        u = User(user_email='hhrty@163.com', password='cat')
        self.assertTrue(u.can(Permission.WRITE_ARTICLES))
        self.assertFalse(u.can(Permission.MODERATE_COMMENTS))
        
    def test_anonymous_user(self):
        u = AnonymousUser()
        self.assertFalse(u.can(Permission.FOLLOW))