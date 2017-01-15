# -*- coding: utf-8 -*-
"""
Created on Wed Jan  4 16:48:11 2017

@author: leo
"""

from  flask import render_template,redirect,request,url_for,flash
from . import auth
from flask_login import login_required,current_user
from ..models import User
from ..email import send_email
from .forms import PasswordResetRequestForm,ChangePasswordForm,PasswordResetForm,ChangeEmailForm
from ..models import db

'''
这里集中了一些用户账户管理的视图
'''
@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        flash('您已经确认了邮件账户。感谢！')
    else:
        flash('邮件账户确认消息过期或无效！')
    return redirect(url_for('main.index'))
        

@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
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
        
    