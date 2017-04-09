# -*- coding: utf-8 -*-
"""
Created on Tue Jan 17 10:46:26 2017

@author: leo
"""
from functools import wraps
from flask import abort
from flask_login import current_user
from .models import Permission

'''
建立修饰器，限制用户访问，部分内容仅对特权用户开放
'''

def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.can(permission):
                abort(403)
            return f(*args,**kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    return permission_required(Permission.ADMINISTER)(f)

"""
漏洞信息编辑
"""
def Vulninfo_editor_required(f):
    return permission_required(Permission.VULNINFO_EDIT)(f)