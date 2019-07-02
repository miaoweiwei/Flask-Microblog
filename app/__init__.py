#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2019/6/22 11:37
@Author  : miaoweiwei
@File    : __init__.py.py
@Software: PyCharm
@Desc    :
"""
import os
import logging
from logging.handlers import SMTPHandler
from logging.handlers import RotatingFileHandler
from flask import Flask, request
from flask_babel import Babel
from flask_babel import lazy_gettext as _l  # 这个新函数将文本包装在一个特殊的对象中，这个对象会在稍后的字符串使用时触发翻译。
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_moment import Moment
from config import Config

app = Flask(__name__)
app.config.from_object(Config)  # 通知Flask读取并使用配置文件
mail = Mail(app)  # 创建邮件实例，该邮件实例用于发送更改密码验证信息
db = SQLAlchemy(app)  # db对象来表示数据库
migrate = Migrate(app, db)  # 数据库迁移引擎migrate
login = LoginManager(app)  # 登录管理初始化
login.login_view = 'login'  # Flask-Login需要知道哪个视图函数用于处理登录认证
# 为了确保这个消息也能被翻译用_l()函数进行延迟处理：
login.login_message = _l('Please log in to access this page.')
bootstrap = Bootstrap(app)  # CSS框架Bootstrap初始化
moment = Moment(app)  # 日期和时间转换成插件格式化
babel = Babel(app)  # Flask-Babel正是用于简化翻译工作的

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
    # 设置每个日志文件10M，总共备份10个日志文件
    file_handler = RotatingFileHandler('logs/microblog.log', maxBytes=1024 * 1024 * 10, backupCount=10)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info('Microblog startup')


# localeselector 装饰器。为每个请求调用装饰器函数以选择用于该请求的语言
# request对象提供了一个高级接口，用于处理客户端发送的带Accept-Language头部的请求。
# 该头部指定了客户端语言和区域设置首选项,该头部的内容可以在浏览器的首选项页面中配置，
# 默认情况下通常从计算机操作系统的语言设置中导入
@babel.localeselector
def get_locale():
    # return request.accept_languages.best_match(app.config['LANGUAGES']) # 会根据浏览器的设置显示语言
    return 'zh'  # 这样会使所有的浏览器都显示为中文


# 下面是一个复杂的Accept-Languages头部的例子：Accept-Language: da, en-gb;q=0.8, en;q=0.7
# 这表示丹麦语（da）是首选语言（默认权重= 1.0），
# 其次是英式英语（en-GB），其权重为0.8，最后是通用英语（en），权重为0.7。
# 要选择最佳语言，你需要将客户请求的语言列表与应用支持的语言进行比较，并使用客户端提供的权重，
# 查找最佳语言。这样做的逻辑有点复杂，但它已经全部封装在best_match()方法中了，
# 该方法将应用提供的语言列表作为参数并返回最佳选择。


# 最下面的导入是解决循环导入的问题，这是Flask应用程序的常见问题。
# 你将会看到routes模块需要导入在这个脚本中定义的app变量，
# 因此将routes的导入放在底部可以避免由于这两个文件之间的相互引用而导致的错误。
from app import routes, models, errors


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
