# -*- coding: utf-8 -*-
"""
Created on Tue Jan  3 10:12:48 2017

@author: leo

This is a app factory .
延迟创建程序实例，之前加载配置项。

"""
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from config import config
from flask_moment import Moment
from flask_login import LoginManager

bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
db = SQLAlchemy()

#flask_login initializing
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'#TODO

#程序生成器
def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)
     #flask-login initializing
    login_manager.init_app(app)
    #To regist the main blueprint
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)    

    #To regist auth blueprint 
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint,url_prefix='/auth')
    #TODO 附加录有何自定义的错误页面  
    
    return app
    