#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2019/6/22 12:44
@Author  : miaoweiwei
@File    : forms.py
@Software: PyCharm
@Desc    : 为了再次践行我的松耦合原则，我会将表单类单独存储到名为app/forms.py的模块中。
就让我们来定义用户登录表单来做一个开始吧，它会要求用户输入username和password，
并提供一个“remember me”的复选框和提交按钮：
"""
from flask_babel import lazy_gettext as _l
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, RadioField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo

from app.models import User


# _() 这个函数静态地把文本翻译成指定的文本
# lazy_gettext 重命名为_l()这个新函数将文本包装在一个特殊的对象中，这个对象会在稍后的字符串使用时触发翻译。

class LoginForm(FlaskForm):
    username = StringField(_l('Username'), validators=[DataRequired()])  # 定义用户名字段
    password = PasswordField(_l('Password'), validators=[DataRequired()])  # 定义密码字段
    remember_me = BooleanField(_l('Remember Me'))  # 定义复选框
    login_type = RadioField(label=_l('Login Type'), choices=(
        ('Administrator', _l('Administrator')),
        ('Customer', _l('Customer'))
    ), default='Administrator')
    submit = SubmitField(_l('Sign In'))  # 定义提交按钮


class RegistrationForm(FlaskForm):
    username = StringField(_l('Username'), validators=[DataRequired()])
    email = StringField(_l('Email'), validators=[DataRequired(), Email()])  # Email()确保输入的内容是Email格式的字符串
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    # EqualTo('password')判断与上一次的输入的password一样
    password2 = PasswordField(_l('Repeat Password'), validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField(_l('Register'))

    # 当添加任何匹配模式validate_ <field_name>的方法时， field_name为字段的名字，
    # WTForms将这些方法作为自定义验证器，并在已设置验证器之后调用它们
    # 本处，我想确保用户输入的username和email不会与数据库中已存在的数据冲突

    def validate_username(self, username):
        """验证用户名是否已经存在"""
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError(_l('Please use a different username.'))

    def validate_email(self, email):
        """验证邮箱是否已经存在"""
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError(_l('Please use a different email address.'))


class ResetPasswordRequestForm(FlaskForm):
    """当用户点击链接时，会出现一个新的Web表单，要求用户输入注册的电子邮件地址，以启动密码重置过程"""
    email = StringField(_l('Email'), validators=[DataRequired(), Email()])
    submit = SubmitField(_l('Request Password Reset'))


class ResetPasswordForm(FlaskForm):
    """重置密码的页面"""
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    password2 = PasswordField(_l('Repeat Password'), validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField(_l('Request Password Reset'))
