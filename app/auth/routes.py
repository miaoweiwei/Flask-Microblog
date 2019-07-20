#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2019/6/22 11:39
@Author  : miaoweiwei
@File    : routes.py
@Software: PyCharm
@Desc    : 
"""

from flask import render_template, flash, redirect, url_for, request
from flask_babel import _
from flask_login import current_user, login_user, logout_user
from werkzeug.urls import url_parse

from app import db
from app.auth import bp
from app.auth.email import send_password_reset_email
from app.auth.forms import LoginForm, ResetPasswordForm
from app.auth.forms import RegistrationForm, ResetPasswordRequestForm
from app.models import User


# 当浏览器向服务器提交表单数据时，通常会使用POST请求（实际上用GET请求也可以，但这不是推荐的做法）。
# 之前的“Method Not Allowed”错误正是由于视图函数还未配置允许POST请求，点击提交按钮时浏览器会发送POST请求
@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:  # 用户已经登录
        return redirect(url_for('main.index'))
    form = LoginForm()
    # 实例方法会执行form校验的工作当浏览器发起GET请求的时候，它返回False，
    # 这样视图函数就会跳过if块中的代码，直接转到视图函数的最后一句来渲染模板，一旦有任意一个字段未通过验证，这个实例方法就会返回False
    if form.validate_on_submit():
        # flash()函数是向用户显示消息的有效途径。 许多应用使用这个技术来让用户知道某个动作是否成功。
        # flash('Login requested for user {}, remember_me={}'.format(form.username.data, form.remember_me.data))
        # flash()显示消息模拟登录，现在我可以真实地登录用户
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash(_('Invalid username or password'))  # 会闪现一条消息到登录界面
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)  # 该函数会将用户登录状态注册为已登录
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')  # redirect()这个函数指引浏览器自动重定向到它的参数所关联的URL
        return redirect(next_page)
    return render_template('auth/login.html', title=_('Sign In'), form=form)  # 此处不能使用 url_for()函数


@bp.route('/logout')
def logout():
    logout_user()  # 用户登出
    return redirect(url_for('main.index'))


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(_('Congratulations, you are now a registered user!'))
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', title=_('Register'), form=form)


@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    """当忘记密码时，点击重置密码的视图函数"""
    if current_user.is_authenticated:  # 首先判断用户是否已经登录
        return redirect(url_for('main.index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()  # 通过用户输入的邮箱地址找到用户
        if user:
            send_password_reset_email(user)
        flash(_('Check your email for the instructions to reset your password'))  # 给出提示
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password_request.html', title=_('Reset Password'), form=form)


@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """重置密码"""
    if current_user.is_authenticated:  # 首先判断用户是否已经登录
        return redirect(url_for('main.index'))
    user = User.verify_reset_password_token(token)  # 验证令牌，获取需要从之密码的用户
    if not user:
        return redirect(url_for('main.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash(_('Your password has been reset.'))
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)
