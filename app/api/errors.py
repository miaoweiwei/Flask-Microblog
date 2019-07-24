#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2019/7/23 13:54
@Author  : miaoweiwei
@File    : errors.py
@Software: PyCharm
@Desc    : errors.py模块将定义一些处理错误响应的辅助函数。
"""
from flask import jsonify
from werkzeug.http import HTTP_STATUS_CODES


# 该函数使用来自Werkzeug（Flask的核心依赖项）的HTTP_STATUS_CODES字典，
# 它为每个HTTP状态代码提供一个简短的描述性名称。
# 我在错误表示中使用这些名称作为error字段的值，
# 所以我只需要操心数字状态码和可选的长描述。
# jsonify()函数返回一个默认状态码为200的FlaskResponse对象，因此在创建响应之后，
# 我将状态码设置为对应的错误代码。
def error_response(status_code, message=None):
    """ 错误处理函数
    :param status_code:
    :param message:
    :return:
    """
    payload = {'error': HTTP_STATUS_CODES.get(status_code, 'Unknown error')}
    if message:
        payload['message'] = message
    response = jsonify(payload)
    response.status_code = status_code
    return response


# API将返回的最常见错误将是代码400，代表了“错误的请求”。
# 这是客户端发送请求中包含无效数据的错误。 为了解决这个更容易产生的错误，
# 我将为它添加一个专用函数，只需传入长的描述性消息作为参数就可以调用。
def bad_request(messga):
    return error_response(400, messga)
