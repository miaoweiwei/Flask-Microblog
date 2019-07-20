#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2019/6/27 12:20
@Author  : miaoweiwei
@File    : email.py
@Software: PyCharm
@Desc    : 简单的电子邮件框架
"""
from flask import render_template, current_app
from flask_babel import _
from app.email import send_email


def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_email(_('[Microblog] Reset Your Password'),
               sender=current_app.config['FLASK_MAIL_SENDER'],  # 邮件发送者
               recipients=[user.email],  # 给用户发送邮件
               text_body=render_template('email/reset_password.txt', user=user, token=token),
               html_body=render_template('email/reset_password.html', user=user, token=token))
