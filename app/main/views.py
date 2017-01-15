# -*- coding: utf-8 -*-
"""
Created on Tue Jan  3 09:48:14 2017

@author: leo
"""

from datetime import datetime
from ..email import send_email
from flask import render_template,session,redirect,url_for,flash,request
from flask_login import login_required,login_user,logout_user,current_user
from . import main
from .forms import LoginForm,RegisterForm
from .. import db
from ..models import User

@main.route('/', methods=['GET','POST'])
def index():
    
    '''
    Topic Feeds
    漏洞精选数据填充
    '''
    topic = {"herf":"http://www.baidu.com","title":"Seebug 漏洞精选第*期","des":"这是 Seebug 精选漏洞第一期!"}
    topics = []
    for i in range(10):
        topics.append(topic)
    '''
    News feeds     
    新闻数据填充
    '''
    new = {"herf":"http://www.baidu.com","title":"黑客事件","des":"德国电信遭黑客攻击：90万路由器下线"}
    news = []
    for i in range(10):
        news.append(new)
  
    loginform = LoginForm()
    userLogin(loginform)
    registerform = RegisterForm()
    render,token = userRegist(registerform)
    
    #@TODO
    #下面用了很笨的方法来重置registerform所有属性
    if token is not None:
        #registerform.reset()
        '''       
        registerform.user_dept=''
        registerform.user_email=''
        registerform.user_name = ''
        registerform.user_pwd = ''
        registerform.user_pwd2 = ''
        '''
        newlogin = LoginForm()       
        newregister = RegisterForm()
        #registerform.register_submit = False
        return render_template('index.html',loginform=newlogin,
                           registerform=newregister,token=token,topics=topics,news=news)
    else:
    #渲染首页模板
        return render_template('index.html',loginform=loginform,
                           registerform=registerform,token=token,topics=topics,news=news)
                           
                   
def userLogin(loginform):
    '''
    用户登录处理
    '''
    if loginform.login_submit.data and loginform.validate_on_submit():
        user = User.query.filter_by(user_email=loginform.user_email.data).first()
        if user is not None and user.verify_password(loginform.user_pwd.data):
            login_user(user,loginform.remenber_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
           
        #flash('用户名或密码输入错误！')        
        
def userRegist(registerform):
    '''
    用户注册处理
    '''
    
    if registerform.register_submit.data and registerform.validate_on_submit():        
        user = User(user_name = registerform.user_name.data,
                    user_email = registerform.user_email.data,
                    password = registerform.user_pwd.data,
                    user_dept = registerform.user_dept.data)
        db.session.add(user)            
        db.session.commit()
        
        token = user.generate_userconfirmation_token()
        send_email(user.user_email,'确认您的邮箱帐户','auth/email/confirm',
                   user=user,token=token)
        
        flash('一封确认邮件已经发送到您的邮箱，请在1小时内点击邮件内链接以确认您的帐户')
        #flash('注册成功，请您登录！')
               
        return redirect(url_for('main.index')),token
    return None,None


@main.route('/logout')
@login_required
def user_logout():
    logout_user()
    return redirect(url_for('main.index'))
    

