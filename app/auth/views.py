# -*- coding: utf-8 -*-
"""
Created on Wed Jan  4 16:48:11 2017

@author: leo
"""

from  flask import render_template,redirect,request,url_for,flash
from . import auth
from flask_login import login_required,current_user,login_user,logout_user
from ..models import User
from ..email import send_email
from .forms import PasswordResetRequestForm,ChangePasswordForm,PasswordResetForm,ChangeEmailForm
from ..models import db
from .forms import LoginForm,RegisterForm

'''
这里集中了一些用户账户管理的视图
'''
@auth.route('/register',methods=['GET','POST'])
def register():
    '''
    用户注册处理
    '''
    registerform = RegisterForm()
    #flask_wtfform提交只是发出post方法，所以必须验证该提交是否有数据
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
               
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html',registerform=registerform)

"""
处理登陆
使用flask_login的login_user维护用户登陆会话
"""
@auth.route('/login',methods=['GET','POST'])
def login():
    '''
    用户登录处理
    '''
    loginform = LoginForm()
    
    if loginform.login_submit.data and loginform.validate_on_submit():
        user = User.query.filter_by(user_email=loginform.user_email.data).first()
        if user is not None and user.verify_password(loginform.user_pwd.data):
            login_user(user,loginform.remenber_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
           
        flash('用户名或密码输入错误！')  
    return render_template('auth/login.html',loginform=loginform)
'''
在用户向本站发送请求时，先检查是否登录，如果登录则更改其近期登录时间（ping）
之后检测当前用户是否未认证邮箱，且是否请求非’auth.‘为首的路由，如果是则转向未认证页面。
'''  
@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()
        if not current_user.user_confirmed and request.endpoint[:5] != 'auth.':
            return redirect(url_for('auth.unconfirmed'))
 
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))
     

@auth.route('/confirm/<token>')
@login_required
def confirm(token): 
    
    if current_user.user_confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        flash('您已经确认了邮件账户。感谢！')
    else:
        flash('邮件账户确认消息过期或无效！')
    return redirect(url_for('main.index'))
    
@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.user_confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')
       

@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_userconfirmation_token()
    send_email(current_user.user_email,'确认您的邮箱帐户','auth/email/confirm',
                   user=current_user,token=token)
    flash('一封确认邮件已经发送到您的邮箱，请在1小时内点击邮件内链接以确认您的帐户')
    return redirect(url_for('main.index'))


@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            db.session.add(current_user)
            flash('您的登录密码已经更新。')
            return redirect(url_for('main.index'))
        else:
            flash('无效的密码。')
    return render_template("auth/change_password.html", form=form)


@auth.route('/reset', methods=['GET', 'POST'])
def password_reset_request():
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = user.generate_reset_token()
            send_email(user.email, '重置您的密码',
                       'auth/email/reset_password',
                       user=user, token=token,
                       next=request.args.get('next'))
        flash('一封含有重置您密码指令的邮件已经发往您的邮箱。 ')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)


@auth.route('/reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            return redirect(url_for('main.index'))
        if user.reset_password(token, form.password.data):
            flash('您的登录密码已经更新。')
            return redirect(url_for('auth.login'))
        else:
            return redirect(url_for('main.index'))
    return render_template('auth/reset_password.html', form=form)


@auth.route('/change-email', methods=['GET', 'POST'])
@login_required
def change_email_request():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            new_email = form.email.data
            token = current_user.generate_email_change_token(new_email)
            send_email(new_email, '确认您的电子邮件账户',
                       'auth/email/change_email',
                       user=current_user, token=token)
            flash('一封含有确认您电子邮件账户指令的邮件已经发往您的邮箱。')
            return redirect(url_for('main.index'))
        else:
            flash('无效的电子邮件账户或密码')
    return render_template("auth/change_email.html", form=form)


@auth.route('/change-email/<token>')
@login_required
def change_email(token):
    if current_user.change_email(token):
        flash('您的电子邮件账户已经被更新。')
    else:
        flash('无效请求。')
    return redirect(url_for('main.index'))
        
    