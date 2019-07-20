#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2019/7/18 21:37
@Author  : miaoweiwei
@File    : __init__.py.py
@Software: PyCharm
@Desc    : 
"""
from flask import Blueprint

bp = Blueprint('auth', __name__)

from app.auth import routes
