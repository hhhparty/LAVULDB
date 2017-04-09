# -*- coding: utf-8 -*-
"""
Created on Tue Jan  3 09:47:42 2017

@author: leo

This is a database model file.
"""
from flask import current_app,request, url_for
from flask_login import UserMixin,AnonymousUserMixin
from werkzeug.security import generate_password_hash,check_password_hash
from . import db, login_manager
from itsdangerous import TimedJSONWebSignatureSerializer
from datetime import datetime
from markdown import markdown
import bleach
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

'''
程序使用权限定义
'''
class Permission:
    FOLLOW = 0x0001
    COMMENT = 0x0002
    WRITE_ARTICLES = 0x0004
    MODERATE_COMMENTS = 0x0008
    VULNINFO_EDIT = 0x0010
    ADMINISTER = 0x0080
  
'''
用户角色模型
'''
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(64), unique=True)
    role_default = db.Column(db.Boolean, default=False, index=True)
    role_permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')
    
    def __repr__(self):
        return '<Role id = %r,role_name=%r,role_default=%r,role_permissions=%r> \n' \
            % (self.id,self.role_name,self.role_default,self.role_permissions)
    
    #自动添加用户角色进入model实例
    @staticmethod
    def insert_roles():
        roles = {
            'User':(Permission.FOLLOW | Permission.COMMENT |
                Permission.WRITE_ARTICLES,True),
            'Moderator':(Permission.FOLLOW | Permission.COMMENT |
                Permission.WRITE_ARTICLES | Permission.MODERATE_COMMENTS,False),
            'Vulninfo_editor':(Permission.FOLLOW | Permission.COMMENT |
                Permission.WRITE_ARTICLES | Permission.MODERATE_COMMENTS |
                Permission.VULNINFO_EDIT,False),
            'Administrator':(0x00ff,False),
        }
        for r in roles:
            role = Role.query.filter_by(role_name=r).first()
            if role is None:
                role = Role(role_name = r)
            role.role_permissions = roles[r][0]
            role.role_default = roles[r][1]
            db.session.add(role)
        db.session.commit()
        

'''
跟帖模型
'''
class Follow(db.Model):
    __tablename__ = 'follows'
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                            primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                            primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    
'''
用户模型
'''        
class User(UserMixin,db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer,primary_key = True)
    user_name = db.Column(db.String(64),unique = True,index = True)
    user_email = db.Column(db.String(200),unique = True,index = True)
    user_pwd_hash = db.Column(db.String(256))#password hash
    user_dept = db.Column(db.String(300))
    user_loc = db.Column(db.String(100))#通信地址
    user_aboutme = db.Column(db.Text())#自我介绍
    user_membersince = db.Column(db.DateTime(),default = datetime.utcnow)#注册时间
    user_lastseen = db.Column(db.DateTime(),default = datetime.utcnow)#最后访问时间
    role_id = db.Column(db.Integer,db.ForeignKey('roles.id'))
    user_confirmed = db.Column(db.Boolean,default=False)    
    posts = db.relationship('Post',backref='author',lazy='dynamic')    
    comments = db.relationship('Comment', backref='author', lazy='dynamic')
    vulninfoes = db.relationship('Vulninfo', backref='editor', lazy='dynamic')
    followed = db.relationship('Follow',
                               foreign_keys=[Follow.follower_id],
                               backref=db.backref('follower', lazy='joined'),
                               lazy='dynamic',
                               cascade='all, delete-orphan')
    followers = db.relationship('Follow',
                                foreign_keys=[Follow.followed_id],
                                backref=db.backref('followed', lazy='joined'),
                                lazy='dynamic',
                                cascade='all, delete-orphan')
 
    def __init__(self,**kwargs):
        super(User,self).__init__(**kwargs)
        
        if self.role is None:
            if self.user_email == current_app.config['LAVULDB_ADMIN']:
                self.role = Role.query.filter_by(role_permissions = 0x00ff).first()
            if self.role is None:
                self.role = Role.query.filter_by(role_default=True).first()
    
    @staticmethod
    def generate_fake(count=5):
        from sqlalchemy.exc import IntegrityError
        from random import seed
        import forgery_py

        seed()
        for i in range(count):
            u = User(user_email=forgery_py.internet.email_address(),
                    user_name=forgery_py.internet.user_name(True),
                    password=forgery_py.lorem_ipsum.word(),
                    user_dept = forgery_py.lorem_ipsum.title(),
                    user_confirmed=True,
                    user_loc=forgery_py.address.city(),
                    user_aboutme=forgery_py.lorem_ipsum.sentence(),
                    user_membersince=forgery_py.date.date(True))
            db.session.add(u)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
        
            
    @staticmethod
    def add_self_follows():
        for user in User.query.all():
            if not user.is_following(user):
                user.follow(user)
                db.session.add(user)
                db.session.commit()
    @staticmethod
    def add_superuser():
        from sqlalchemy.exc import IntegrityError
        from datetime import datetime
        admin = User(user_email="hhhparty@163.com",
                    user_name="lihao",
                    password="123",
                    user_dept = "zgy",
                    user_confirmed=True,
                    user_loc="beijing",
                    user_aboutme="haha",
                    user_membersince=datetime.now())
        db.session.add(admin)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
    def can(self,permissions):
        return self.role is not None and (self.role.role_permissions & permissions) == permissions
    
    def is_administrator(self):
        return self.can(Permission.ADMINISTER)
        
    
    def __repr__(self):
        return '\n<User id=%r,user_name=%r,user_email=%r,user_pwd_hash=%r,user_confirmed=%r,user_dept=%r,role_id=%r>\n' % (self.id ,self.user_name,self.user_email,self.user_pwd_hash,self.user_confirmed,self.user_dept,self.role_id)
        
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
        return s.dumps({'confirm':self.id})
        
    def confirm(self,token): 
        s = TimedJSONWebSignatureSerializer(current_app.config['SECRET_KEY'])
          
        try:
            data = s.loads(token)  
        except:
            print("TimedJSONWebSignatureSerializer loads error!")
            return False        
        if data.get('confirm') != self.id:
            print(data.get('confirm'))
            return False
        self.user_confirmed = True
        db.session.add(self)
        db.session.commit()
        return True
        
    def ping(self):
        self.user_lastseen = datetime.utcnow()
        db.session.add(self)
        db.session.commit()
    def follow(self, user):
        if not self.is_following(user):
            f = Follow(follower=self, followed=user)
            db.session.add(f)

    def unfollow(self, user):
        f = self.followed.filter_by(followed_id=user.id).first()
        if f:
            db.session.delete(f)

    def is_following(self, user):
        return self.followed.filter_by(
            followed_id=user.id).first() is not None

    def is_followed_by(self, user):
        return self.followers.filter_by(
            follower_id=user.id).first() is not None

    @property
    def followed_posts(self):
        return Post.query.join(Follow, Follow.followed_id == Post.author_id)\
            .filter(Follow.follower_id == self.id)

    def to_json(self):
        json_user = {
            'url': url_for('api.get_user', id=self.id, _external=True),
            'username': self.username,
            'member_since': self.member_since,
            'last_seen': self.last_seen,
            'posts': url_for('api.get_user_posts', id=self.id, _external=True),
            'followed_posts': url_for('api.get_user_followed_posts',
                                      id=self.id, _external=True),
            'post_count': self.posts.count()
        }
        return json_user

   
        
"""  
匿名用户模型
"""    
class AnonymousUser(AnonymousUserMixin):    
    def can(self,permissions):
        return False
    
    def is_administrator(self):
        return False
    def is_anonymoususer(self):
        return True
    
        
   
    def ping(self):
        pass
    def __repr__(self):
        return '\n AnonymousUser'
        
login_manager.anonymous_user = AnonymousUser


'''
用户文章模型
'''
class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    comments = db.relationship('Comment', backref='post', lazy='dynamic')

    @staticmethod
    def generate_fake(count=100):
        from random import seed, randint
        import forgery_py

        seed()
        user_count = User.query.count()
        for i in range(count):
            u = User.query.offset(randint(0, user_count - 1)).first()
            p = Post(body=forgery_py.lorem_ipsum.sentences(randint(1, 5)),
                     timestamp=forgery_py.date.date(True),
                     author=u)
            db.session.add(p)
            db.session.commit()

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p']
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True))

    def to_json(self):
        json_post = {
            'url': url_for('api.get_post', id=self.id, _external=True),
            'body': self.body,
            'body_html': self.body_html,
            'timestamp': self.timestamp,
            'author': url_for('api.get_user', id=self.author_id,
                              _external=True),
            'comments': url_for('api.get_post_comments', id=self.id,
                                _external=True),
            'comment_count': self.comments.count()
        }
        return json_post

    @staticmethod
    def from_json(json_post):
        body = json_post.get('body')
        if body is None or body == '':
            raise ValidationError('post does not have a body')
        return Post(body=body)


db.event.listen(Post.body, 'set', Post.on_changed_body)

'''
用户评论模型
'''     
class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    disabled = db.Column(db.Boolean)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'code', 'em', 'i',
                        'strong']
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True))

    def to_json(self):
        json_comment = {
            'url': url_for('api.get_comment', id=self.id, _external=True),
            'post': url_for('api.get_post', id=self.post_id, _external=True),
            'body': self.body,
            'body_html': self.body_html,
            'timestamp': self.timestamp,
            'author': url_for('api.get_user', id=self.author_id,
                              _external=True),
        }
        return json_comment

    @staticmethod
    def from_json(json_comment):
        body = json_comment.get('body')
        if body is None or body == '':
            raise ValidationError('comment does not have a body')
        return Comment(body=body)


db.event.listen(Comment.body, 'set', Comment.on_changed_body)          
'''
漏洞影响软件列表模型
'''
class Vulnsoftwarelist(db.Model):
    __tablename__ = 'vulnsoftwarelists'
    id = db.Column(db.Integer, primary_key=True)
    product = db.Column(db.String(200),index=True)
    vulninfo_id = db.Column(db.Integer,db.ForeignKey('vulninfoes.id'))
    
    def __repr__(self):
       return '\n<Vulnsoftwarelist id=%r,product=%r>' % \
           (self.id,self.product)

   
'''
漏洞严重性模型
'''    
class Vulnseverity(db.Model):
    __tablename__ = "vulnseverities"
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(100),unique = True,index = True)
    description = db.Column(db.String(100))
    vulninfoes = db.relationship('Vulninfo', backref='vulnseverity', lazy='dynamic')
    
    def __repr__(self):
        return '\n<VulnSeverity id=%r,name=%r,description=%r>' % (self.id,self.name,self.description)
     #自动添加漏洞类型进入VulnSeverity实例
    @staticmethod
    def insert_vulnseverity():
        vulnseverities = {
            "super_dangerous":"超危",
            "high_dangerous":"高危",
            "middle_dangerous":"中危",
            "low_dangerous":"低危",
            "unknown":"未知",
        }
        for s in vulnseverities:
            vulnseverity = Vulnseverity.query.filter_by(name=s).first()
            if vulnseverity is None:
                vulnseverity = Vulnseverity(name=s)
            vulnseverity.description = vulnseverities[s]
            db.session.add(vulnseverity)
        db.session.commit()
        
'''
漏洞影响实体描述模型


描述规范：CNCPE:/{部件}:{生产厂商}:{产品名称}:{产品版本}:{更新版本}:{适用版本}:{界面语言}
CNCPE:/｛part｝:｛vendor｝:｛product｝:｛version｝:｛update｝:｛edition｝:｛language｝ 

部件分为三类：硬件（Hardware）、操作系统（Operating system）和应用程序（Application）。
1、中文表达形式为：硬件、操作系统、应用。例如：CNCPE:/应用:北京智通:网际快车:3.5:::中文-台湾
2、英文表达形式为：h、o、a。例如：CNCPE:/a:acme:product:1.0:update2:-:en-us 

生产厂商名称通常采用生产厂商的注册域名进行命名.


逻辑连接符号
出于漏洞影响实体组成的复杂性，及漏洞影响的产品和版本多样性，上面的基本描述结构不能满足部分漏洞所影响的产品。
用“AND”（同时满足）、“OR”（满足任一）、“NOT”（不满足）三个逻辑连接符号连接不同的基本结构。
如果结构比较复杂，则可以用小括号表示安全级。

实例：
<cncpe negate="false" operator="OR">
    <cncpe-lang name="cpe:/a:pivotal_software:redis:2.8.23"/>
    <cncpe-lang name="cpe:/o:debian:debian_linux:8.0"/>
    <cncpe-lang name="cpe:/a:pivotal_software:redis:3.0.2"/>
    <cncpe-lang name="cpe:/a:pivotal_software:redis:3.0.3"/>
    <cncpe-lang name="cpe:/a:pivotal_software:redis:3.0.4"/>
    <cncpe-lang name="cpe:/a:pivotal_software:redis:3.0.5"/>
    <cncpe-lang name="cpe:/a:pivotal_software:redis:3.0.1"/>
    <cncpe-lang name="cpe:/a:pivotal_software:redis:3.0.0"/>
</cncpe>
'''    
class Cncpe(db.Model):
    __tablename__ ="cncpes"
    id = db.Column(db.Integer,primary_key=True)
    part = db.Column(db.String(300))
    vendor = db.Column(db.String(300))
    product = db.Column(db.String(300))
    version = db.Column(db.String(200))
    update = db.Column(db.String(200))
    edition = db.Column(db.String(200))
    language = db.Column(db.String(200))
    cncpeoperator = db.Column(db.String(100))#TODO： thinking
    vulninfo_id = db.Column(db.Integer,db.ForeignKey('vulninfoes.id'))
    
    def __repr__(self):
        return '\n<Cncpe id=%r,part=%r,vendor=%r,product=%r,version=%r, update=%r,edition=%r,language=%r,vulninfo=%r>' % (self.id,self.part,self.vendor,self.product,self.version, self.update,self.edition,self.language,self.vulninfo)
    
    """
    input usage:"cpe:/a:pivotal_software:redis:2.8.23"
    """    
    def cncpeNameParse(self,cncpelangName):
        l = cncpelangName.split(":")
        for i in range(len(l)):
            if i == 1:
                self.part = l[1][1]#get the ｛part｝
            if i == 2:
                self.vendor = l[2]
            if i == 3:
                self.product = l[3]
            if i == 4:
                self.version = l[4]
            if i == 5:
                self.update = l[5]
            if i == 6:
                self.edition = l[6]
            if i == 7:
                self.language = l[7]
           
        
    
'''
漏洞参考
'''
class Vulnref(db.Model):
    __tablename__ = 'vulnrefs'
    id = db.Column(db.Integer,primary_key=True)    
    ref_source = db.Column(db.String(300))#漏洞信息相关网站的网址。
    ref_name = db.Column(db.String(300))#漏洞信息相关网站的名称。
    ref_url = db.Column(db.String(300))#定 义：漏洞信息相关的网址。    
    vulninfo_id = db.Column(db.Integer,db.ForeignKey('vulninfoes.id'))
    
    def __repr__(self):
        return '\n<Vulnref id=%r,ref_source=%r,ref_name=%r,ref_url=%r, vulninfo=%r>' \
            % (self.id,self.ref_source,self.ref_name,self.ref_url,self.vulninfo)

   
'''
漏洞信息模型
'''            
class Vulninfo(db.Model):
    __tablename__ = 'vulninfoes'
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(200), nullable=False) #漏洞名称
    vuln_id = db.Column(db.String(100),index=True)#漏洞编号，格式"(CNNVD)\-\d\d\d\d\\d\d-\d\d\d\d"/
    published = db.Column(db.DateTime())#漏洞发布时间
    modified = db.Column(db.DateTime())#漏洞更新时间
    source = db.Column(db.String(200)) #发布漏洞的单位全称。
    severity = db.Column(db.Integer,db.ForeignKey('vulnseverities.id'))#漏洞危害等级,引用vulnseverity对象   
    vulntype_id = db.Column(db.Integer,db.ForeignKey('vulntypes.id'))#漏洞类型    
    vulntype_alias_id = db.Column(db.Integer,db.ForeignKey('vulntypes.id'))#漏洞类型
    vulnconf = db.relationship('Cncpe', backref='vulninfo', lazy='dynamic')#漏洞所影响实体的信息，包括厂商、产品名称和版本号等。
    vulnsoftwares = db.relationship('Vulnsoftwarelist', backref='vulninfo', lazy='dynamic')#影响的产品信息
    vuln_descript = db.Column(db.Text())#漏洞描述需要说明的相关信息，例如漏洞产生的具体原因。
    vuln_exploit = db.Column(db.Text())#漏洞利用的方法，例如漏洞攻击方案或利用代码。
    cve_id =  db.Column(db.String(100))#漏洞的 cve 编号。
    bugtraq_id =  db.Column(db.String(100))#漏洞的 Bugtraq 编号。
    cnnvd_id =  db.Column(db.String(100))#漏洞的 cnnvd编号。
    vuln_solution = db.Column(db.Text())#漏洞的解决方案，例如补丁信息等。。
    vuln_refs = db.relationship('Vulnref',backref='vulninfo',lazy='dynamic')#漏洞信息相关信息
    editor_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    def __repr__(self):
        return '\n<Vulninfo id=%r,name=%r,vuln_id=%r,cnnvd_id=%r,published=%r,modified=%r,source=%r>'\
            % (self.id ,self.name,self.vuln_id,self.cnnvd_id,self.published,self.modified,self.source)
    
 
'''
漏洞类型模型
'''    

class Vulntype(db.Model):
    __tablename__ = 'vulntypes'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100),unique = True,index = True)
    description = db.Column(db.String(100))
       
    vulninfoes = db.relationship('Vulninfo',
                               foreign_keys=[Vulninfo.vulntype_id],
                               backref=db.backref('vulntype', lazy='joined'),
                               lazy='dynamic')
    vulninfoes_alias = db.relationship('Vulninfo',
                                foreign_keys=[Vulninfo.vulntype_alias_id],
                                backref=db.backref('vulntype_alias', lazy='joined'),
                                lazy='dynamic')
    
    def __repr__(self):
        return '\n<VulnType id=%r, name=%r,description=%r>' % (self.id,self.name,self.description)
  
    #自动添加漏洞类型进入vulntypes实例
    @staticmethod
    def insert_vulntypes():
        vulntypes = {
            "code":"代码",
            "sourcecode":"源代码",
            "dataprocess":"数据处理",
            "inputvalidation":"输入验证",
            "commandinjection":"命令注入",
            "oscommandinjection":"操作系统命令注入",
            "sqlinjection":"SQL注入",
            "xss":"跨站脚本",
            "codeinjection":"代码注入",
            "pathequivalence":"路径等价",
            "pathtraverse":"路径遍历",
            "postlink":"后置链接",
            "digitalerror":"数字错误",
            "infomgrterror":"信息管理错误",
            "infoleakage":"信息泄露",
            "resourcemgrterror":"资源管理错误",
            "buffoverflow":"缓冲区溢出",
            "formatstring":"格式化字符串",
            "injection":"注入",
            "competecondition":"竞争条件",
            "securityfeature":"安全特征/功能",
            "csrf":"跨站请求伪造",
            "insufficientvalidationdataauth":"未充分验证数据权限",
            "trustmgrt":"信任管理",
            "authaceesscontrol":"权限许可和访问控制",
            "authorizationproblem":"授权问题",
            "encryptionproblem":"加密问题",
            "accesscontrolerror":"访问控制错误",
            "configerror":"配置错误",
            "insufficientinformation":"资料不足",
            "other":"其他",
        }
        for vt in vulntypes:
            vulntype = Vulntype.query.filter_by(name=vt).first()
            if vulntype is None:
                vulntype = Vulntype(name = vt)
            vulntype.description = vulntypes[vt]
            db.session.add(vulntype)
        db.session.commit()
 