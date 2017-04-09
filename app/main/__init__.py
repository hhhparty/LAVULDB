"""
Created on Tue Jan  3 10:12:48 2017

@author: leo

This is a app blueprint .

A blueprint is an object that records functions
 that will be called with the BlueprintSetupState later to register functions 
 or other things on the main application. 

"""

from flask import Blueprint

main = Blueprint('main',__name__)

'''
Importing views,errors, and connect the blueprint and these views.
The next import must be file tail, avoiding to repeatly import flask,etc.
'''

from . import views,errors,forms

'''
模板中可能会检查权限，把Permission类加入上下文管理器
'''
from ..models import Permission
@main.app_context_processor
def inject_permissions():
    return dict(Permission = Permission)