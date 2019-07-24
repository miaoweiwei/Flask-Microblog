#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2019/7/24 9:36
@Author  : miaoweiwei
@File    : auth.py
@Software: PyCharm
@Desc    :
当你编写一个API时，你必须考虑到你的客户端并不总是要连接到Web应用程序的Web浏览器。
当独立客户端（如智能手机APP）甚至是基于浏览器的单页应用程序访问后端服务时，
API展示力量的机会就来了。 当这些专用客户端需要访问API服务时，他们首先需要请求token，
对应传统Web应用程序中登录表单的部分。
Flask-HTTPAuth支持几种不同的认证机制，都对API友好。 首先，我将使用HTTPBasic Authentication，
该机制要求客户端在标准的Authorization头部中附带用户凭证。 要与Flask-HTTPAuth集成，
应用需要提供两个函数：一个用于检查用户提供的用户名和密码，另一个用于在认证失败的情况下返回错误响应。
这些函数通过装饰器在Flask-HTTPAuth中注册，然后在认证流程中根据需要由插件自动调用。
"""
from flask import g
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth

from app.models import User
from app.api.errors import error_response

basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth()

"""
Flask-HTTPAuth的HTTPBasicAuth类实现了基本的认证流程。 这两个必需的函数分别通过verify_password和error_handler装饰器进行注册。
验证函数接收客户端提供的用户名和密码，如果凭证有效则返回True，否则返回False。 我依赖User类的check_password()方法来检查密码，
它在Web应用的认证过程中，也会被Flask-Login使用。 我将认证用户保存在g.current_user中，以便我可以从API视图函数中访问它。


错误处理函数只返回由app/api/errors.py模块中的error_response()函数生成的401错误。
401错误在HTTP标准中定义为“未授权”错误。
HTTP客户端知道当它们收到这个错误时，需要重新发送有效的凭证。
"""


@basic_auth.verify_password
def verify_password(username, password):
    user = User.query.filter_by(username=username).first()
    if user is None:
        return False
    g.current_user = user
    return user.check_password(password)


@basic_auth.error_handler
def basic_auth_error():
    return error_response(401)


"""
使用token认证时，Flask-HTTPAuth使用的是verify_token装饰器注册验证函数，除此之外，token认证的工作方式与基本认证相同。
我的token验证函数使用User.check_token()来定位token所属的用户。 该函数还通过将当前用户设置为None来处理缺失token的情况。
返回值是True还是False，决定了Flask-HTTPAuth是否允许视图函数的运行。
"""


@token_auth.verify_token
def verify_token(token):
    g.current_user = User.check_token(token) if token else None
    return g.current_user is not None


@token_auth.error_handler
def token_auth_error():
    return error_response(401)
