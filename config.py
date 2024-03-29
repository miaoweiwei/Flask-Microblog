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
import uuid
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))  # 该应用程序的根目录
# 创建一个 .env 文件并在其中写入应用所需的所有环境变量了
# 不要将 .env 文件加入到源代码版本控制中，这非常重要。否则，一旦你的密码和其他重要信息上传到远程代码库中后，你就会后悔莫及.
# .env文件可以用于所有配置变量，但是不能用于Flask命令行的FLASK_APP和FLASK_DEBUG环境变量，
# 因为它们在应用启动的早期（应用实例和配置对象存在之前）就被使用了。
load_dotenv(os.path.join(basedir, '.env'))  # 不能存放对Flask设置的配置


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'  # Post请求不能少
    # SECRET_KEY = uuid.uuid4().hex  # 可以使用UUID生成随机的字符串
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
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')  # 账号和密码最好放在环境变量中，放在这里容易泄露密码 该密码要到qq邮箱的设置中开启 POP3/SMTP 和 IMAP/SMTP
    FLASK_MAIL_SENDER = '1353263604@qq.com'

    SEND_MAIL = False

    # 表示主页每页展示的数据列表长度
    POSTS_PER_PAGE = 25

    # 跟踪支持的语言列表
    LANGUAGES = ['zh', 'en', 'es']  # 中文，英文，西班牙文

    MS_TRANSLATE_KEY = os.environ.get("MS_TRANSLATE_KEY")  # 获取微软翻译api的key ，搞半天没有申请下来，还是用百度的吧

    # 百度翻译的 appid和秘钥
    BAIDU_TRANSLATE_APPID = os.environ.get("BAIDU_TRANSLATE_APPID")
    BAIDU_TRANSLATE_SECRET = os.environ.get("BAIDU_TRANSLATE_SECRET")

    # Elasticsearch 配置。用于搜索服务
    # 如果变量未定义，我将设置其为None，并将其用作禁用Elasticsearch的信号,环境变量写在了.env文件中
    ELASTICSEARCH_URL = os.environ.get('ELASTICSEARCH_URL') or None
    # ELASTICSEARCH_URL = 'http://localhost:9200'
