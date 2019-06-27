#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2019/6/22 11:37
@Author  : miaoweiwei
@File    : __init__.py.py
@Software: PyCharm
@Desc    :
"""
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from logging.handlers import SMTPHandler
from logging.handlers import RotatingFileHandler
import os
import logging
from config import Config

app = Flask(__name__)
app.config.from_object(Config)  # 通知Flask读取并使用配置文件
mail = Mail(app)  # 创建邮件实例，该邮件实例用于发送更改密码验证信息
db = SQLAlchemy(app)  # db对象来表示数据库
migrate = Migrate(app, db)  # 数据库迁移引擎migrate
login = LoginManager(app)  # 登录管理初始化
login.login_view = 'login'  # Flask-Login需要知道哪个视图函数用于处理登录认证
bootstrap = Bootstrap(app)  # CSS框架Bootstrap初始化

# 最下面的导入是解决循环导入的问题，这是Flask应用程序的常见问题。
# 你将会看到routes模块需要导入在这个脚本中定义的app变量，
# 因此将routes的导入放在底部可以避免由于这两个文件之间的相互引用而导致的错误。
from app import routes, models, errors

if not app.debug:
    if app.config['MAIL_SERVER']:
        auth = None
        if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
            auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        secure = None
        if app.config['MAIL_USE_TLS']:
            secure = ()

        mailhost = (app.config['MAIL_SERVER'], app.config['MAIL_PORT'])
        fromaddr = app.config['MAIL_USERNAME']
        toaddrs = app.config['ADMINS']
        subject = "Microblog Failure"
        credentials = auth
        mail_handler = SMTPHandler(mailhost, fromaddr, toaddrs, subject,
                                   credentials=credentials,
                                   secure=secure,
                                   timeout=10)
        # 设置要发送邮件日志的格式
        mail_handler.setFormatter(logging.Formatter('[%(asctime)s] %(levelname)s in %(module)s: %(message)s'))
        mail_handler.setLevel(logging.ERROR)  # 设置级别
        mail_handler.set_name("failure email")  # 设置该条日志配置的名称
        app.logger.addHandler(mail_handler)

    # 记录日志
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/microblog.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info('Microblog startup')
