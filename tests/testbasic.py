# -*- coding: utf-8 -*-
"""
Created on Tue Jan  3 11:02:23 2017

@author: leo
"""

import unittest
from flask import current_app
from app import create_app,db

class BasicTestCase(unittest.TestCase):
    #下面的函数测试前自动执行，用于创建测试环境
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
     #下面的函数测试后自动执行   
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    #测试当前app是否成功创建。test_开头的都要测试
    def test_app_exists(self):
        self.assertFalse(current_app is None)
    # 测试当前配置是否为TESTING
    def test_app_is_testing(self):
        self.assertTrue(current_app.config['TESTING'])
        