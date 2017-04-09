# -*- coding: utf-8 -*-
"""
Created on Tue Jan  3 09:50:09 2017

@author: leo
@email:hhhparty@163.com

This is global configure file of la vuldb project.
It configs base dir ,database path ,wtf secret key,etc.
"""

import os
import logging
import time

basedir = os.path.abspath(os.path.dirname(__file__))
#Define the logger
logger = logging.getLogger("LAVULNDB_PORJECT")
logger.setLevel(logging.DEBUG)
logger_fh = logging.FileHandler(time.strftime("%Y%m%d",time.localtime())+".log")
logger_fh.setLevel(logging.DEBUG)
logger_ch = logging.StreamHandler()
logger_ch.setLevel(logging.ERROR)
formatter = logging.Formatter("%(asctime)s-%(name)s-%(levelname)s-%(message)s")
logger_fh.setFormatter(formatter)
logger_ch.setFormatter(formatter)
logger.addHandler(logger_fh)
logger.addHandler(logger_ch)

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'wds.doie.edu.cn' 
    SQLALCHEMY_ON_TEARDOWN=True #数据更新即提交  
    SQLALCHEMY_TRACK_MODIFICATIONS = True #2.0中替代了SQLALCHEMY_ON_TEARDOWN
    LAVULDB_MAIL_SUBJECT_PREFIX = '[LAVULDB]'
    LAVULDB_MAIL_SENDER = 'LAVULDB Admin <admin@exampl.com>'
    LAVULDB_ADMIN = os.environ.get('LAVULDB_ADMIN') or 'hhhparty@163.com'
    
    MAIL_SERVER = 'smtp.g.com'#TODO 未定邮件服务器
    MAIL_PORT = 587 #TODO 未定邮件服务器
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_SERVER = 'smtp.g.com'
    MAIL_PORT = 587
    LAVULDB_MAIL_SUBJECT_PREFIX = '[LAVULDB]'
    LAVULDB_MAIL_SENDER = 'LAVULDB Admin <LAVULDB@example.com>'
    LAVULDB_SLOW_DB_QUERY_TIME=2
    
    
    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True    
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
		'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
		'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
		'sqlite:///' + os.path.join(basedir, 'data.sqlite')

config = {
    'development':DevelopmentConfig,
    'testing':TestConfig,
    'production':ProductionConfig,
    
    'default':DevelopmentConfig
}
