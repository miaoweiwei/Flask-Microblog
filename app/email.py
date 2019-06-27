#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2019/6/27 12:20
@Author  : miaoweiwei
@File    : email.py
@Software: PyCharm
@Desc    : 简单的电子邮件框架
"""
from threading import Thread

from flask import render_template
from flask_mail import Message
from app import app, mail


def send_email(subject, sender, recipients, text_body, html_body):
    """
    发送邮件
    :param subject:主题
    :param sender:发送者
    :param recipients:收件人列表
    :param text_body:
    :param html_body:
    """
    msg = Message(subject=subject,
                  recipients=recipients,
                  body=text_body,
                  html=html_body,
                  sender=sender)
    # msg = Message(subject, sender, recipients)
    # msg.body = text_body
    # msg.html = html_body
    # Thread(target=send_async_email, args=(app, msg)).start()  # 使用后台线程去发送邮件
    mail.send(msg)


def send_async_email(app, msg):
    """异步的去发送邮件"""
    with app.app_context():
        mail.send(msg)


def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_email('[Microblog] Reset Your Password',
               sender=app.config['FLASK_MAIL_SENDER'],  # 邮件发送者
               recipients=[user.email],  # 给用户发送邮件
               text_body=render_template('email/reset_password.txt', user=user, token=token),
               html_body=render_template('email/reset_password.html', user=user, token=token))
