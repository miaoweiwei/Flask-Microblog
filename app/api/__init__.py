#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2019/7/23 12:16
@Author  : miaoweiwei
@File    : __init__.py.py
@Software: PyCharm
@Desc    : api模块
"""

from flask import Blueprint

bp = Blueprint('api', __name__)

from app.api import users, errors, tokens
# 需要将导入移动到底部以避免循环依赖错误
