# -*- coding: utf-8 -*-
"""
Created on Tue Jan  3 15:35:45 2017

@author: leo
"""

import unittest
from app.models import User

class UserModelTestCase(unittest.TestCase):
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