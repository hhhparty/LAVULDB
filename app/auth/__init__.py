# -*- coding: utf-8 -*-
"""
Created on Tue Jan  3 15:12:59 2017

@author: leo
"""
from flask import Blueprint

auth = Blueprint('auth',__name__)

from . import views
