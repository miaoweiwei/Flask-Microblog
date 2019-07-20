#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2019/7/19 9:47
@Author  : miaoweiwei
@File    : __init__.py.py
@Software: PyCharm
@Desc    : 
"""
from flask import Blueprint

bp = Blueprint('main', __name__)

from app.main import routes
