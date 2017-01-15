# -*- coding: utf-8 -*-
"""
Created on Wed Jan  4 17:07:51 2017

@author: leo
"""

'''
用户修改信息类表单
'''

from flask_wtf import Form
from wtforms import StringField,PasswordField,SubmitField
from wtforms.validators import InputRequired,Email,Length,EqualTo
from wtforms import ValidationError
from ..models import User 


class ChangePasswordForm(Form):
    old_password = PasswordField('原始密码', validators=[InputRequired()])
    password = PasswordField('新密码', validators=[
        InputRequired(), EqualTo('password2', message='Passwords must match')])
    password2 = PasswordField('重复新密码', validators=[InputRequired()])
    submit = SubmitField('确定更改')


class PasswordResetRequestForm(Form):
    email = StringField('电子邮件', validators=[InputRequired(), Length(1, 64),
                                             Email()])
    submit = SubmitField('重置密码')


class PasswordResetForm(Form):
    email = StringField('电子邮件', validators=[InputRequired(), Length(1, 64),
                                             Email()])
    password = PasswordField('新密码', validators=[
        InputRequired(), EqualTo('password2', message='两次输入必须一致')])
    password2 = PasswordField('重复新密码', validators=[InputRequired()])
    submit = SubmitField('确定更改')

    def validate_email(self, field):
        if User.query.filter_by(user_email=field.data).first() is None:
            raise ValidationError('未知的邮件地址。')


class ChangeEmailForm(Form):
    email = StringField('新电子邮件', validators=[InputRequired(), Length(1, 64),
                                                 Email()])
    password = PasswordField('密码', validators=[InputRequired()])
    submit = SubmitField('更新电子邮件地址')

    def validate_email(self, field):
        if User.query.filter_by(user_email=field.data).first():
            raise ValidationError('该电子邮件帐号已经被注册。')