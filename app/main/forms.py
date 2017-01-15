# -*- coding: utf-8 -*-
"""
Created on Tue Jan  3 09:48:43 2017

@author: leo
"""


from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField,PasswordField,BooleanField
from wtforms.validators import InputRequired,Email,Length,EqualTo,Regexp
from wtforms import ValidationError
from ..models import User

class LoginForm(FlaskForm):
    user_email = StringField('电子邮件：',
                             validators=[InputRequired(),Length(1,64),Email()])
    user_pwd = PasswordField('登录密码：',validators=[InputRequired()])
    remenber_me = BooleanField('记住我')
    login_submit = SubmitField('确定登录')
    
    
class RegisterForm(FlaskForm):
    user_name = StringField('用户名：',
                    validators=[InputRequired('用户名是必填内容'),Length(1,64),
                        Regexp('^[A-Za-z][A-Za-z0-9_.]*$',0,
                               '用户名仅能由英文字母,数字，点或下划线组成')])
    user_email = StringField('电子邮件：',
                      validators=[InputRequired(),
                                  Email("请输入正确的邮件地址"),Length(1,64)])
    user_pwd = PasswordField('登录密码：',
                    validators=[InputRequired(),Length(1,64),
                        EqualTo('user_pwd2',message='两次密码的输入相同！')])
    user_pwd2 =  PasswordField('确认登录密码：',
                               validators=[InputRequired(),Length(1,64)])
    user_dept = StringField('单位名：',
                            validators=[InputRequired(),Length(1,200)])
    register_submit = SubmitField('确定注册')
    '''
    以validate_命名的自定义验证函数，可以与上面字段定义中的validators同时自动被调用，
    完成验证。
    '''
    def validate_user_email(self,field):
        if User.query.filter_by(user_email=field.data).first():
            raise ValidationError('该Email邮箱已经被注册，请使用其他Email注册！')
    def validate_user_name(self,field):
        if User.query.filter_by(user_name=field.data).first():
            raise ValidationError('该用户名已经被注册，请使用其他用户名注册！')
    def reset(self):
        self.user_name = ''
        self.user_email = ''
        self.user_pwd = ''
        self.user_pwd2 = ''
        self.user_dept = ''
        self.register_submit = False
        
        