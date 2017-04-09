# -*- coding: utf-8 -*-
"""
Created on Tue Jan  3 09:48:43 2017

@author: leo
"""
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SelectField, \
    SubmitField,DateField
from wtforms.validators import InputRequired, Length, Email, Regexp
from wtforms import ValidationError
from flask_pagedown.fields import PageDownField
from ..models import Role, User,Vulntype,Vulnseverity,Vulninfo

class EditUserProfileForm(FlaskForm):
    user_name = StringField('用户名：',
                    validators=[InputRequired('用户名是必填内容'),Length(1,64),
                        Regexp('^[A-Za-z][A-Za-z0-9_.]*$',0,
                               '用户名仅能由英文字母,数字，点或下划线组成')])
    user_loc = StringField('通信地址', validators=[Length(0, 64)])   
    user_dept = StringField('单位名：', \
                validators=[InputRequired('单位信息是必填内容'),Length(1,200)]) 
    user_aboutme = TextAreaField('自我介绍')
    submit = SubmitField('确认更新')

class EditUserProfileAdminForm(FlaskForm):
    user_email = StringField('电子邮件：',
                      validators=[InputRequired(),
                                  Email("请输入正确的邮件地址"),Length(1,64)])
    user_confirmed = BooleanField('电子邮件账户确认')
    role = SelectField('用户角色',coerce=int)
    user_name = StringField('用户名：',
                    validators=[InputRequired('用户名是必填内容'),Length(1,64),
                        Regexp('^[A-Za-z][A-Za-z0-9_.]*$',0,
                               '用户名仅能由英文字母,数字，点或下划线组成')])
    user_loc = StringField('通信地址', validators=[Length(0, 64)])   
    user_dept = StringField('单位名：',
                            validators=[InputRequired('单位信息是必填内容'), \
                                Length(1,200)]) 
    user_aboutme = TextAreaField('自我介绍')
    submit = SubmitField('确认更新')
    
    def __init__(self,user,*args,**kwargs):
        super(EditUserProfileAdminForm,self).__init__(*args,**kwargs)
        self.role.choices = [(role.id,role.role_name)
            for role in Role.query.order_by(Role.role_name).all()]
        self.user = user
        
    
    '''
    以validate_命名的自定义验证函数，可以与上面字段定义中的validators同时自动被调用，
    完成验证。
    '''
    def validate_user_email(self,field):
        if field.data != self.user.user_email and \
                User.query.filter_by(user_email=field.data).first():
            raise ValidationError('该Email邮箱已经被注册，请使用其他Email注册！')
    def validate_user_name(self,field):
        if field.data != self.user.user_name and \
                User.query.filter_by(user_name=field.data).first():
            raise ValidationError('该用户名已经被注册，请使用其他用户名注册！')
            
            
class PostForm(FlaskForm):
    body = TextAreaField('今天写点什么......',validators=[InputRequired()])
    submit = SubmitField('保存')
    
    
###################vulnerability field#######################
    

"""
Cncpe Form
漏洞影响实体描述表单
"""
class CncpeForm(FlaskForm):

    part = TextAreaField('部件',validators=[InputRequired()])
    vendor = TextAreaField('生产厂商',validators=[InputRequired()])
    product = TextAreaField('产品名称',validators=[InputRequired()])
    version = TextAreaField('产品版本',validators=[InputRequired()])
    update = TextAreaField('更新版本',validators=[InputRequired()])
    edition = TextAreaField('适用版本',validators=[InputRequired()])
    language =TextAreaField('界面语言',validators=[InputRequired()])
    cncpeoperator = TextAreaField('operator',validators=[InputRequired()])#TODO： thinking
    submit = SubmitField('提交')
    
class VulnrefForm(FlaskForm):
    ref_source = TextAreaField('来源',validators=[InputRequired()])
    ref_name = TextAreaField('名字',validators=[InputRequired()])
    ref_url = TextAreaField('网址',validators=[InputRequired()])   
    submit = SubmitField('提交')    
    
    
class VulntypeForm(FlaskForm):
    name = TextAreaField('名字',validators=[InputRequired()])
    description = TextAreaField('类型描述',validators=[InputRequired()])   
    submit = SubmitField('提交') 
    
    
class VulnseverityForm(FlaskForm):
    name = TextAreaField('名字',validators=[InputRequired()])
    description = TextAreaField('严重性描述',validators=[InputRequired()])   
    submit = SubmitField('提交') 
"""
Name: Vulninfo Form
Description:漏洞信息表单
"""
class VulninfoForm(FlaskForm):
    name = StringField('漏洞名称：',
                    validators=[InputRequired('漏洞名称是必填内容'),Length(1,200),
                        Regexp('^[A-Za-z][A-Za-z0-9_.]*$',0,
                               '漏洞名称仅能由英文字母,数字，点或下划线组成')])
    vuln_id = StringField('漏洞编号：',
                    validators=[InputRequired('漏洞编号是必填内容'),Length(1,200),
                        Regexp('^LAVD-\d\d\d\d-\d\d\d\d$',0, \
                        '漏洞编号格式为：格式LAVD-\d\d\d\d-\d\d\d\d')])
    published = DateField('发布时间：',
                            validators=[InputRequired('发布时间是必填内容'),\
                                Length(1,20)],
                            )
    modified = DateField('更新时间：',
                            validators=[InputRequired('更新时间是必填内容'),\
                                Length(1,20)])
    source = StringField('漏洞来源：',validators=[Length(1,100)])
    severity = SelectField('危害等级：',coerce=int)
    vuln_type = SelectField('漏洞类型：',coerce=int)
    vuln_type_alias = SelectField('漏洞类型别名：',coerce=int)       
    #vulnerable_configuration = 
    #vuln_softwarelist = 
    vuln_descript = TextAreaField('漏洞描述：')
    vuln_exploit = TextAreaField('利用方法：')
    cve_id = StringField('CVE编号：', validators=[Length(1,200)])
    bugtraq_id = StringField('Bugtraq编号：', validators=[Length(1,200)])
    cnnvd_id = StringField('CNNVD编号：', validators=[Length(1,200)])
    vuln_solution = TextAreaField('解决方案：')
    #vuln_refs = 
    submit = SubmitField('保存')
    
    
    def __init__(self,*args,**kwargs):
        super(VulninfoForm,self).__init__(*args,**kwargs)
        
        self.severity.choices = [(vulnseverity.id,vulnseverity.description)
            for vulnseverity in Vulnseverity.query.order_by(Vulnseverity.name).all()]
                
        self.vuln_type.choices = [(vulntype.id,vulntype.description)
            for vulntype in Vulntype.query.order_by(Vulntype.name).all()]
                
        self.vuln_type_alias.choices = [(vulntype.id,vulntype.description)
            for vulntype in Vulntype.query.order_by(Vulntype.name).all()]
        
        
    '''
    以validate_命名的自定义验证函数，可以与上面字段定义中的validators同时自动被调用，
    完成验证。
    '''    
    def validate_name(self,field):
        if Vulninfo.query.filter_by(name=field.data).first():
            raise ValidationError('以当前漏洞名称命名的漏洞信息已经存在！')
    def validate_vuln_id(self,field):
        if Vulninfo.query.filter_by(vuln_id=field.data).first():
            raise ValidationError('以当前漏洞编号命名的漏洞信息已经存在！')
                
###################vulnerability field#######################