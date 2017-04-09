# -*- coding: utf-8 -*-
"""
Created on Tue Jan  3 09:48:04 2017

@author: leo

This file handles errors as a view fuction.
"""

from flask import render_template,request, jsonify
from . import main


'''
The decorater app_errorhandler can trigger global error handler function.
The decorater errorhandler can only trigger blueprint handler function.
'''
#loginform = LoginForm()
#registerform = RegisterForm()
#,loginform = loginform ,registerform=registerform
@main.app_errorhandler(404)
def page_not_found(e):
    
    return render_template('404.html'),404

@main.app_errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'),500
    
@main.app_errorhandler(403)
def forbidden(e):
    if request.accept_mimetypes.accept_json and \
            not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'forbidden'})
        response.status_code = 403
        return response
    return render_template('403.html'), 403

