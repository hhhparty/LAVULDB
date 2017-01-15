# -*- coding: utf-8 -*-
"""
Created on Tue Jan  3 09:47:42 2017

@author: leo

This is a database model file.
"""
from flask import current_app
from flask_login import UserMixin,AnonymousUserMixin
from werkzeug.security import generate_password_hash,check_password_hash
from . import db, login_manager
from itsdangerous import TimedJSONWebSignatureSerializer

'''
flask-login要求定义的回调函数，此处用于加载登录用户
该函数接收以unicode字符串形式的用户标识符。如果能找到用户，
则返回用户对象，否则返回None
'''

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


"""
Define Models
"""
class Permission:
    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE_ARTICLES = 0x04
    MODERATE_COMMENTS = 0x08
    ADMINISTER = 0x80


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(64), unique=True)
    role_default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')
    
    def __repr__(self):
        return '<Role %r>' % self.role_name
        
class User(UserMixin,db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer,primary_key = True)
    user_name = db.Column(db.String(64),unique = True,index = True)
    user_email = db.Column(db.String(200),unique = True,index = True)
    user_pwd_hash = db.Column(db.String(256))#password hash
    user_dept = db.Column(db.String(300))
    role_id = db.Column(db.Integer,db.ForeignKey('roles.id'))
    user_confirmed = db.Column(db.Boolean,default=False)
    
    def __repr__(self):
        return '\n<User id=%r,user_name=%r,user_email=%r,user_pwd_hash=%r,user_dept=%r,role_id=%r>\n' % (self.id ,self.user_name,self.user_email,self.user_pwd_hash,self.user_dept,self.role_id)
        
    @property
    def password(self):
        raise AttributeError('Password is not a readable attribute')
    
    @password.setter
    def password(self,password):
        self.user_pwd_hash = generate_password_hash(password)
        
    def verify_password(self,password):
        return check_password_hash(self.user_pwd_hash,password)
    
    def generate_userconfirmation_token(self,expiration=3600):
        s = TimedJSONWebSignatureSerializer(current_app.config['SECRET_KEY'],expiration)
        return s.dumps({'user_confirm':self.id})
    def confirm(self,token):
        s = TimedJSONWebSignatureSerializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('user_confirm') != self.id:
            return False
        self.user_confirmed = True
        db.session.add(self)
        return True
        
        
'''
if __name__ == '__main__':
    pass
    #db.drop_all()
    #db .create_all()
    #print(User.query.all())
 
    admin_role = Role(role_name='Admin')
    mod_role = Role(role_name = 'Moderator')
    user_role = Role(role_name = 'User')
    user_join = User(user_name='john',role=admin_role)
    user_susan = User(user_name = 'susan',role=user_role)
    user_david = User(user_name = 'david',role = user_role)
    
    db.session.add(admin_role)
    db.session.add(mod_role)
    db.session.add(user_role)
    db.session.add(user_join)
    db.session.add(user_susan)
    db.session.add(user_david)
    
    db.session.commit()
        
    print(User.query.all())
    print(Role.query.all())
    
    print(User.query.filter_by(username='john').all())
'''
    