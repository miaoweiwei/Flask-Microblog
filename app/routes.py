#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2019/6/22 11:39
@Author  : miaoweiwei
@File    : routes.py
@Software: PyCharm
@Desc    : 
"""

from flask import render_template, flash, redirect, url_for, request, g
from flask_login import current_user, login_user, logout_user, login_required
from flask_babel import _, get_locale
from werkzeug.urls import url_parse
from datetime import datetime
from app import app
from app.email import send_password_reset_email
from app.forms import LoginForm, PostForm, ResetPasswordForm
from app.models import User, Post
from app import db
from app.forms import RegistrationForm, EditProfileForm, ResetPasswordRequestForm


# 当浏览器向服务器提交表单数据时，通常会使用POST请求（实际上用GET请求也可以，但这不是推荐的做法）。
# 之前的“Method Not Allowed”错误正是由于视图函数还未配置允许POST请求，点击提交按钮时浏览器会发送POST请求
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:  # 用户已经登录
        return redirect(url_for('index'))
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
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)  # 该函数会将用户登录状态注册为已登录
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')  # redirect()这个函数指引浏览器自动重定向到它的参数所关联的URL
        return redirect(next_page)
    return render_template('login.html', title=_('Sign In'), form=form)  # 此处不能使用 url_for()函数


@app.route('/logout')
def logout():
    logout_user()  # 用户登出
    return redirect(url_for('index'))


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required  # 该装饰器来拒绝匿名用户的访问以保护某个视图函数。 当你将此装饰器添加到位于@app.route装饰器下面的视图函数上时，该函数将受到保护，不允许未经身份验证的用户访问
def index():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash(_('Your post is now live!'))
        return redirect(url_for('index'))
    # User类的followed_posts方法返回一个SQLAlchemy查询对象，该对象被配置为从数据库中获取用户感兴趣的用户动态。
    # 在这个查询中调用all()会触发它的执行，返回值是包含所有结果的列表
    start_page = request.args.get('page', 1, type=int)  # 获取动态页要显示动态的起始页
    end_page = app.config['POSTS_PER_PAGE']  # 获取动态页要显示动态的终止页
    # posts = current_user.followed_posts().all()  # 获取当前用户的主页应该显示的所有动态

    # paginate()获取指定起始和终止页的动态，
    # 错误处理布尔标记，如果是True，当请求范围超出已知范围时自动引发404错误。如果是False，则会返回一个空列表。
    # 返回一个Pagination的实例 用于分页
    # 其items属性是请求内容的数据列表。Pagination实例还有一些其他用途
    posts = current_user.followed_posts().paginate(start_page, end_page, False)
    next_url = url_for('index', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('index', page=posts.prev_num) if posts.has_prev else None
    return render_template("index.html", title=_('Home'), form=form,
                           posts=posts.items,
                           next_url=next_url,
                           prev_url=prev_url)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(_('Congratulations, you are now a registered user!'))
        return redirect(url_for('login'))
    return render_template('register.html', title=_('Register'), form=form)


@app.route('/User/<username>')
@login_required  # 只能被已登录的用户访问
def user(username):
    """用户视图"""
    user = User.query.filter_by(username=username).first_or_404()
    strart_page = request.args.get('page', 1, type=int)
    end_page = app.config['POSTS_PER_PAGE']
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(strart_page, end_page, False)
    next_url = url_for('user', username=user.usernmae, page=posts.next_num) if posts.has_next else None
    prev_url = url_for('user', username=user.usernmae, page=posts.prev_num) if posts.has_prev else None

    return render_template('user.html', user=user,
                           posts=posts.items,
                           next_url=next_url,
                           prev_url=prev_url)


# @app.before_request注册在视图函数之前执行的函数因为现在我可以在一处地方编写代码，
# 并让它在任何视图函数之前被执行
@app.before_request
def before_request():
    """简单地实现了检查current_user是否已经登录,并在已登录的情况下将last_seen字段设置为当前时间"""
    if current_user.is_authenticated:  # 当前用户是否已经登录
        current_user.last_seen = datetime.utcnow()
        db.session.commit()  # 不需要db.session.add()这句，因为当前用户已经存在数据库里了，当前用户是查询得到的
    g.locale = str(get_locale())


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():  # 提交用户更新的数据
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()  # 提交更新用户信息
        flash(_('Your changes have been saved.'))  # 提示
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':  # 如果它是GET，这是初始请求的情况
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title=_('Edit Profile'), form=form)


@app.route('/follow/<username>')
@login_required
def follow(username):
    """关注一个用户"""
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(_('User %(username)s not found.', username=username))
        return redirect(url_for('index'))
    if user == current_user:
        flash(_('You cannot follow yourself!'))
        return redirect(url_for('user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash(_('You are following %(username)s!', username=username))
    return redirect(url_for('user', username=username))


@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    """取消关注某个用户"""
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(_('User %(username)s not found.', username=username))
        return redirect(url_for('index'))
    if user == current_user:
        flash(_('You cannot unfollow yourself!'))
        return redirect(url_for('user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash(_('You are not following %(username)s.', username=username))
    return redirect(url_for('user', username=username))


@app.route('/explore')
def explore():
    """发现页面的视图
       主页和发现页是同一个页面，只不过做了不同的处理
    """
    start_page = request.args.get('page', 1, type=int)  # 获取动态页要显示动态的起始页
    end_page = app.config['POSTS_PER_PAGE']  # 获取动态页要显示动态的终止页
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(start_page, end_page, False)

    next_url = url_for('explore', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('explore', page=posts.prev_num) if posts.has_prev else None
    # 但与主页不同的是，在发现页面不需要一个发表用户动态表单，
    # 所以在这个视图函数中，我没有在模板调用中包含form参数。
    return render_template('index.html', title=_("Explore"),
                           posts=posts.items,
                           next_url=next_url,
                           prev_url=prev_url)


@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    """当忘记密码时，点击重置密码的视图函数"""
    if current_user.is_authenticated:  # 首先判断用户是否已经登录
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()  # 通过用户输入的邮箱地址找到用户
        if user:
            send_password_reset_email(user)
        flash(_('Check your email for the instructions to reset your password'))  # 给出提示
        return redirect(url_for('login'))
    return render_template('reset_password_request.html', title=_('Reset Password'), form=form)


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:  # 首先判断用户是否已经登录
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)  # 验证令牌，获取需要从之密码的用户
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash(_('Your password has been reset.'))
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)
