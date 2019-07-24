#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2019/7/18 21:24
@Author  : miaoweiwei
@File    : handlers.py
@Software: PyCharm
@Desc    : 
"""
from flask import render_template, request
from app import db
from app.errors import bp
from app.api.errors import error_response as api_error_response

"""
在本章的前部分，当我要求你用一个无效的用户URL从浏览器发送一个API请求时发生了什么?服务器返回了404错误，
但是这个错误被格式化为标准的404 HTML错误页面。在API blueprint中的API可能返回的许多错误可以被重写为JSON版本，
但是仍然有一些错误是由Flask处理的，处理这些错误的处理函数是被全局注册到应用中的，返回的是HTML。

HTTP协议支持一种机制，通过该机制，客户机和服务器可以就响应的最佳格式达成一致，称为内容协商。
客户端需要发送一个Accept头部，指示格式首选项。然后，服务器查看自身格式列表并使用匹配客户端格
式列表中的最佳格式进行响应。

我想做的是修改全局应用的错误处理器，使它们能够根据客户端的格式首选项对返回内容是使用HTML还是JSON进行内容协商。
这可以通过使用Flask的request.accept_mimetypes来完成:

ants_json_response()辅助函数比较客户端对JSON和HTML格式的偏好程度。 如果JSON比HTML高，
那么我会返回一个JSON响应。 否则，我会返回原始的基于模板的HTML响应。 对于JSON响应，
我将使用从API blueprint中导入error_response辅助函数，但在这里我要将其重命名为api_error_response()，
以便清楚它的作用和来历。
"""


def wants_json_response():
    return request.accept_mimetypes['application/json'] >= request.accept_mimetypes['text/html']


@bp.app_errorhandler(404)
def not_found_error(error):
    if wants_json_response():
        return api_error_response(404)
    return render_template('errors/404.html'), 404  # 404是错误代码，不加第二个参数默认是200表示成功响应的状态码


@bp.app_errorhandler(500)
def internal_error(error):
    db.session.rollback()
    if wants_json_response():
        return api_error_response(500)
    return render_template('errors/500.html'), 500
