#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2019/6/22 12:37
@Author  : miaoweiwei
@File    : config.py
@Software: PyCharm
@Desc    : 
"""
import os

basedir = os.path.abspath(os.path.dirname(__file__))  # 该应用程序的根目录


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'  # Post请求不能少
    # Flask-SQLAlchemy插件从SQLALCHEMY_DATABASE_URI配置变量中获取应用的数据库的位置
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'app.db')
    # SQLALCHEMY_TRACK_MODIFICATIONS配置项用于设置数据发生变更之后是否发送信号给应用，我不需要这项功能，因此将其设置为False。
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 设置邮件，当服务出现错误时给我发邮件，有关配置是读取的环境变量
    # 有关环境变量的设置例如：设置MAIL_SERVER在Terminal里使用 set MAIL_SERVER = smtp.qq.com
    # MAIL_SERVER = os.environ.get('MAIL_SERVER')  # 服务器
    # MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)  # 端口 587 发送日志和使用Message发送都将可以使用这种方式 465只能使用Message发送邮件
    # MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None  # TLS 发送日志和使用Message发送都将可以使用这种方式
    # MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL') is not None  # SSL加密 使用Message发送可以，发送日志不行
    # MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    # MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    # FLASKY_MAIL_SENDER = os.environ.get('FLASKY_MAIL_SENDER')  # 邮件的发送者
    ADMINS = ['1353263604@qq.com', '1000460675 @ smail.shnu.edu.cn']  # ADMINS配置变量是将收到错误报告的电子邮件地址列表

    MAIL_SERVER = 'smtp.qq.com'  # 服务器
    MAIL_USE_SSL = False
    MAIL_USE_TLS = True  # TLS 发送日志使用这种方式使用Message发送邮件也可以使用这种方式
    MAIL_PORT = 587
    MAIL_USERNAME = '1353263604@qq.com'
    MAIL_PASSWORD = 'uhuobgoaynquhdeb'  # 该密码要到qq邮箱的设置中开启 POP3/SMTP 和 IMAP/SMTP
    FLASK_MAIL_SENDER = '1353263604@qq.com'

    # 表示主页每页展示的数据列表长度
    POSTS_PER_PAGE = 25

    # 跟踪支持的语言列表
    LANGUAGES = ['zh', 'en', 'es']  # 中文，英文，西班牙文

    # Elasticsearch 配置。
    # ELASTICSEARCH_URL = os.environ.get('ELASTICSEARCH_URL')  # 如果变量未定义，我将设置其为None，并将其用作禁用Elasticsearch的信号
    ELASTICSEARCH_URL = 'http: // localhost: 5000'
