#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2019/7/18 21:24
@Author  : miaoweiwei
@File    : handlers.py
@Software: PyCharm
@Desc    : 
"""
from flask import render_template
from app import db
from app.errors import bp


@bp.app_errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404  # 404是错误代码，不加第二个参数默认是200表示成功响应的状态码


@bp.app_errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500
