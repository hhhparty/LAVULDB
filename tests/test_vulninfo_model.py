#-*- coding: utf-8 -*-
"""
Created on Tue Jan  3 15:35:45 2017

@author: leo
"""
import unittest
import time
from datetime import datetime
from app import create_app, db
from app.models import User, AnonymousUser, Role, Permission
from app.models import Vulninfo,Vulntype,Vulnref,Cncpe,Vulnseverity,Vulnsoftwarelist


class VulninfoModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()
        Vulntype.insert_vulntypes()
        Vulnseverity.insert_vulnseverity()        
        u = User(user_name='lihao',user_email='hhhparty@163.com')
        db.session.add(u)
        db.session.commit()
        self.editor = User.query.filter_by(user_email='hhhparty@163.com').first()

    #tearDown函数在测试后自动执行   
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop() 
        
    def test_vulninfo_insert(self):
        desc = "Redis是美国Redis Labs公司赞助的一套开源的使用ANSI C编写、支持网络、可基于内存亦可持久化的日志型、键值（Key-Value）存储数据库，并提供多种语言的API。 Redis 2.8.24之前2.8.x版本和3.0.6之前3.0.x版本的lua_struct.c文件中的‘getnum’函数存在整数溢出漏洞。远程攻击者可借助较大的数字利用该漏洞造成拒绝服务（内存损坏和应用程序崩溃）。"
        solution = '目前厂商已经发布了升级补丁以修复此安全问题，详情请关注厂商主页： http://redis.io/'
        vulninfo = Vulninfo(name='Redis 整数溢出漏洞' , 
                    vuln_id ='LAVD-2016-0001', 
                    published = datetime.strptime("2016-04-14",'%Y-%m-%d'), 
                    modified = datetime.strptime("2016-04-14",'%Y-%m-%d'),
                    source ='Luca Bruno' ,
                    severity = Vulnseverity.query.filter_by(description='中危').first().id ,
                    vuln_type_id = Vulntype.query.filter_by(description ='数字错误').first().id,
                    vuln_type_alias_id = Vulntype.query.filter_by(description ='输入验证').first().id,
                    vuln_descript = desc,
                    vuln_exploit = '未知',    
                    cve_id =  'CVE-2015-8080', 
                    bugtraq_id = '77507',
                    cnnvd_id = 'CNNVD-201511-360',
                    vuln_solution = solution, 
                    editor_id = self.editor.id )
        db.session.add(vulninfo)
        db.session.commit()
        vi = Vulninfo.query.filter_by(vuln_id ='LAVD-2016-0001').first()
        self.assertTrue(vi.published.year == 2016)
        self.assertTrue(vi.modified.month == 4)
        self.assertTrue(Vulnseverity.query.filter_by(id=vi.severity).first().description == '中危')
        self.assertTrue(Vulntype.query.filter_by(id =vi.vuln_type_id).first().description == '数字错误')
        
        
    
        