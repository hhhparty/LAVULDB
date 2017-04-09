# -*- coding: utf-8 -*-
"""
Created on Tue Jan  3 09:48:14 2017

@author: leo
"""

from flask import render_template, redirect, url_for, abort, flash, request,\
    current_app, make_response
from . import main
from flask_sqlalchemy import get_debug_queries
from .forms import EditUserProfileForm,EditUserProfileAdminForm,PostForm,\
    VulninfoForm,CncpeForm,VulnrefForm,VulntypeForm,VulnseverityForm
from flask_login import login_required,current_user,login_user,logout_user
from ..decorators import admin_required, permission_required,\
    Vulninfo_editor_required
from ..models import db,Role, User,Permission,Post,Vulninfo,AnonymousUser,\
    Vulnref,Cncpe,Vulntype


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
   
    #渲染首页模板
    return render_template('index.html',topics=topics,news=news)                      
                   
@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(user_name = username).first()
    if user is None:
        abort(404)
    return render_template('user.html',user = user)

@main.after_app_request
def after_request(response):
    for query in get_debug_queries():
        if query.duration >= current_app.config['LAVULDB_SLOW_DB_QUERY_TIME']:
            current_app.logger.warning(
                'Slow query: %s\nParameters: %s\nDuration: %fs\nContext: %s\n'
                % (query.statement, query.parameters, query.duration,
                   query.context))
    return response
    
@main.route('/shutdown')
def server_shutdown():
    if not current_app.testing:
        abort(404)
    shutdown = request.environ.get('werkzeug.server.shutdown')
    if not shutdown:
        abort(500)
    shutdown()
    return 'Shutting down...'
    
@main.route('/edit_userprofile',methods=['GET','POST'])
@login_required
def edit_userprofile():
    form = EditUserProfileForm()
    if form.submit.data and form.validate_on_submit():
        current_user.user_name = form.user_name.data
        current_user.user_loc = form.user_loc.data
        current_user.user_aboutme = form.user_aboutme.data
        current_user.user_dept = form.user_dept.data
        db.session.add(current_user)
        db.session.commit()
        
        flash('你的个人资料已经被更新.')
        return redirect(url_for('.user',username=current_user.user_name))
    
    form.user_name.data = current_user.user_name
    form.user_dept.data = current_user.user_dept
    form.user_loc.data = current_user.user_loc
    form.user_aboutme.data = current_user.user_aboutme
    return render_template('edit_userprofile.html',form=form)
    
@main.route('/edit_userprofile/<int:id>',methods=['GET','POST'])
@login_required
@admin_required
def edit_userprofile_admin(id):
    user = User.query.get_or_404(id)
    form = EditUserProfileAdminForm(user=user)
    
    if form.submit.data and form.validate_on_submit():
        user.user_name = form.user_name.data
        user.user_email = form.user_email.data
        user.user_confirmed = form.user_confirmed.data
        user.role = Role.query.get(form.role.data)        
        user.user_loc = form.user_loc.data
        user.user_aboutme = form.user_aboutme.data
        user.user_dept = form.user_dept.data
        
        db.session.add(user)
        db.session.commit()
        
        flash('用户个人资料已经被更新.')
        return redirect(url_for('.user',username=user.user_name))
    
    form.user_email.data = user.user_email
    form.user_confirmed.data = user.user_confirmed
    form.role.data = user.role_id 
    form.user_name.data = user.user_name
    form.user_dept.data = user.user_dept
    form.user_loc.data = user.user_loc
    form.user_aboutme.data = user.user_aboutme
    return render_template('edit_userprofile.html',form=form,user=user)
    

@main.route('/post',methods=['GET','POST'])
def post():
    form = PostForm()
    if current_user.can(Permission.WRITE_ARTICLES) and \
            form.submit.data and form.validate_on_submit():
        post = Post(body=form.body.data,author=current_user._get_current_object())
        db.session.add(post)
        db.session.commit()
        
        return redirect(url_for('main.post'))
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    
    return render_template('post.html',form=form,posts=posts)

"""
漏洞影响实体
"""
@main.route('/cncpe',methods=['GET','POST'])#done
def cncpe():

    form = CncpeForm()
    if form.submit.data and form.validate_on_submit():
        app = Cncpe(part=form.part.data,
                    vendor=form.vendor.data,
                    product=form.product.data,
                    version=form.version.data,
                    update=form.update.data,
                    edition=form.edition.data,
                    language=form.language.data,
                    cncpeoperator=form.cncpeoperator.data)

        db.session.add(app)            
        db.session.commit()
        

        return redirect(url_for('main.index'))        
        flash('check the data have been added into data.sqlite?')
     
    
    return render_template('cncpe.html',form=form)
    
"""
漏洞相关情况    
""" 
@main.route('/vulnref',methods=['GET','POST'])
def vulnref():

    form =VulnrefForm()
    if form.submit.data and form.validate_on_submit():
        app = Vulnref(ref_source=form.ref_source.data,
                       ref_name=form.ref_name.data,
                       ref_url=form.ref_url.data)

        db.session.add(app)            
        db.session.commit()
        

        return redirect(url_for('main.index'))        
        flash('check the data have been added into data.sqlite?')
     
    
    return render_template('vulnref.html',form=form)    
    
    
"""
漏洞类型
"""    
@main.route('/vulntype',methods=['GET','POST'])
def vulntype():
    form = VulntypeForm()
    if form.submit.data and form.validate_on_submit():
        app = Vulntype(name=form.name.data,
                       description=form.description.data)

        db.session.add(app)            
        db.session.commit()
        
        return redirect(url_for('main.index'))
        
        flash('check the data wheather have been added into data.sqlite again!')
        
     
    
    return render_template('vulntype.html',form=form)	
    

'''
漏洞危害程度
'''
@main.route('/vulnseverity',methods=['GET','POST'])
def vulnseverity():
    form = VulnseverityForm()
    if form.submit.data and form.validate_on_submit():
        app = Vulntype(name=form.name.data,
                       description=form.description.data)

        db.session.add(app)            
        db.session.commit()
        
        return redirect(url_for('main.index'))
        
        flash('check the data wheather have been added into data.sqlite again!')
        
     
    
    return render_template('vulnseverity.html',form=form)	
 
'''
漏洞信息显示
'''
@main.route('/vulninfo', methods=['GET','POST'])
def vulninfo():   
    vulninfoes = Vulninfo.query.order_by(Vulninfo.published.desc()).all()    
    return render_template('vulninfo.html',form=None,vulninfoes=vulninfoes)
  
'''
漏洞信息录入
'''
@main.route('/vulninfoinsert', methods=['GET','POST'])
@login_required
@Vulninfo_editor_required
def vulninfoinsert():   
    form = VulninfoForm()
    if current_user.can(Permission.VULNINFO_EDIT) and \
            form.submit.data and form.validate_on_submit():
        vulninfo = Vulninfo(name=form.name.data, \
                            vuln_id = form.vuln_id.data, \
                            published = form.published.data, \
                            modified = form.modified.data, \
                            source = form.source.data, \
                            severity = form.severity.data, \
                            vuln_type_id = form.vuln_type.data, \
                            vuln_type_alias_id = form.vuln_type_alias.data, \
                            vuln_type = form.vuln_id.data, \
                            vuln_type_alias =form.vuln_id.data, \
                            vuln_descript = form.vuln_descript.data, \
                            vuln_exploit = form.vuln_exploit.data, \
                            cve_id =  form.cve_id.data, \
                            bugtraq_id =  form.bugtraq_id.data, \
                            cnnvd_id = form.cnnvd_id.data, \
                            vuln_solution = form.vuln_solution.data, \
                            editor_id = current_user._get_current_object())      
        
        db.session.add(vulninfo)
        db.session.commit()
        
        return redirect(url_for('main.vulninfoinsert'))
    #vulninfoes = Vulninfo.query.order_by(Vulninfo.published.desc()).all()
    
    return render_template('vulninfoinsert.html',form=form)
    
"""
漏洞库管理
"""
@main.route('/vulndbmgmt',methods=['GET','POST'])
@login_required
@admin_required
def vulndbmgmt():
    vulninfoes = Vulninfo.query.all()
    return render_template('vulndbmgmt.html',vulninfoes=vulninfoes)