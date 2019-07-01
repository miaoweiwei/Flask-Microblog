#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2019/6/25 9:46
@Author  : miaoweiwei
@File    : errors.py
@Software: PyCharm
@Desc    : 自定义错误页面的视图
"""
from flask import render_template
from app import app, db


@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404  # 404是错误代码，不加第二个参数默认是200表示成功响应的状态码


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500
