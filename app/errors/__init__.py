#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2019/7/18 21:24
@Author  : miaoweiwei
@File    : __init__.py.py
@Software: PyCharm
@Desc    : 
"""
from flask import Blueprint

bp = Blueprint('errors', __name__)  # 基础模块的名称（通常在Flask应用实例中设置为__name__）

# 导入了handlers.py模块，以便其中的错误处理程序在blueprint中注册。 该导入位于底部以避免循环依赖。
from app.errors import handlers
