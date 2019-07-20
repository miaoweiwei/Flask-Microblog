#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2019/7/19 9:48
@Author  : miaoweiwei
@File    : routes.py
@Software: PyCharm
@Desc    : 
"""

# @bp.before_request注册在视图函数之前执行的函数因为现在我可以在一处地方编写代码，
# 并让它在任何视图函数之前被执行
from datetime import datetime

from flask import render_template, flash, redirect, url_for, request, g, jsonify, current_app
from flask_babel import _, get_locale
from flask_login import current_user, login_required
from guess_language import guess_language

from app import db
from app.main import bp
from app.main.forms import EditProfileForm, PostForm, SearchForm
from app.models import User, Post
from app.translate import baidu_translate


@bp.before_app_request
def before_request():
    """简单地实现了检查current_user是否已经登录,并在已登录的情况下将last_seen字段设置为当前时间"""
    if current_user.is_authenticated:  # 当前用户是否已经登录
        current_user.last_seen = datetime.utcnow()
        db.session.commit()  # 不需要db.session.add()这句，因为当前用户已经存在数据库里了，当前用户是查询得到的
        g.search_form = SearchForm()
    g.locale = str(get_locale())


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required  # 该装饰器来拒绝匿名用户的访问以保护某个视图函数。 当你将此装饰器添加到位于@bp.route装饰器下面的视图函数上时，该函数将受到保护，不允许未经身份验证的用户访问
def index():
    form = PostForm()
    if form.validate_on_submit():
        language = guess_language(form.post.data)  # 获取动态的语言类型
        if language == 'UNKNOWN' or len(language) > 5:
            language = ''
        post = Post(body=form.post.data, author=current_user, language=language)
        db.session.add(post)
        db.session.commit()
        flash(_('Your post is now live!'))
        return redirect(url_for('main.index'))
    # User类的followed_posts方法返回一个SQLAlchemy查询对象，该对象被配置为从数据库中获取用户感兴趣的用户动态。
    # 在这个查询中调用all()会触发它的执行，返回值是包含所有结果的列表
    start_page = request.args.get('page', 1, type=int)  # 获取动态页要显示动态的起始页
    end_page = current_app.config['POSTS_PER_PAGE']  # 获取动态页要显示动态的终止页
    # posts = current_user.followed_posts().all()  # 获取当前用户的主页应该显示的所有动态

    # paginate()获取指定起始和终止页的动态，
    # 错误处理布尔标记，如果是True，当请求范围超出已知范围时自动引发404错误。如果是False，则会返回一个空列表。
    # 返回一个Pagination的实例 用于分页
    # 其items属性是请求内容的数据列表。Pagination实例还有一些其他用途
    posts = current_user.followed_posts().paginate(start_page, end_page, False)
    next_url = url_for('main.index', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('main.index', page=posts.prev_num) if posts.has_prev else None
    # 上一条语句的url_for里要加上main，因为它返回的是指向视图的路径，下面的不用加main，因为index.html不在main文件夹里
    return render_template('index.html', title=_('Home'), form=form,
                           posts=posts.items, next_url=next_url, prev_url=prev_url)


@bp.route('/explore')
def explore():
    """发现页面的视图
       主页和发现页是同一个页面，只不过做了不同的处理
    """
    start_page = request.args.get('page', 1, type=int)  # 获取动态页要显示动态的起始页
    end_page = current_app.config['POSTS_PER_PAGE']  # 获取动态页要显示动态的终止页
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(start_page, end_page, False)

    next_url = url_for('main.explore', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('main.explore', page=posts.prev_num) if posts.has_prev else None
    # 但与主页不同的是，在发现页面不需要一个发表用户动态表单，
    # 所以在这个视图函数中，我没有在模板调用中包含form参数。
    return render_template('index.html', title=_("Explore"),
                           posts=posts.items,
                           next_url=next_url,
                           prev_url=prev_url)


@bp.route('/User/<username>')
@login_required  # 只能被已登录的用户访问
def user(username):
    """用户视图"""
    user = User.query.filter_by(username=username).first_or_404()
    strart_page = request.args.get('page', 1, type=int)
    end_page = current_app.config['POSTS_PER_PAGE']
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(strart_page, end_page, False)
    next_url = url_for('main.user', username=user.username, page=posts.next_num) if posts.has_next else None
    prev_url = url_for('main.user', username=user.username, page=posts.prev_num) if posts.has_prev else None
    return render_template('user.html', user=user, posts=posts.items, next_url=next_url, prev_url=prev_url)


@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():  # 提交用户更新的数据
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()  # 提交更新用户信息
        flash(_('Your changes have been saved.'))  # 提示
        return redirect(url_for('main.edit_profile'))
    elif request.method == 'GET':  # 如果它是GET，这是初始请求的情况
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title=_('Edit Profile'), form=form)


@bp.route('/follow/<username>')
@login_required
def follow(username):
    """关注一个用户"""
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(_('User %(username)s not found.', username=username))
        return redirect(url_for('main.index'))
    if user == current_user:
        flash(_('You cannot follow yourself!'))
        return redirect(url_for('main.user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash(_('You are following %(username)s!', username=username))
    return redirect(url_for('main.user', username=username))


@bp.route('/unfollow/<username>')
@login_required
def unfollow(username):
    """取消关注某个用户"""
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(_('User %(username)s not found.', username=username))
        return redirect(url_for('main.index'))
    if user == current_user:
        flash(_('You cannot unfollow yourself!'))
        return redirect(url_for('main.user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash(_('You are not following %(username)s.', username=username))
    return redirect(url_for('main.user', username=username))


@bp.route('/translate', methods=['POST'])
@login_required
def translate_text():
    # ms_dic = {'text': ms_translate(request.form['text'],
    #                                request.form['source_language'],
    #                                request.form['dest_language'])}
    baidu_dic = {'text': baidu_translate(request.form['text'],
                                         request.form['source_language'],
                                         request.form['dest_language'])}
    return jsonify(baidu_dic)


@bp.route('/search')
@login_required
def search():
    """用于搜索的视图函数"""
    if not g.search_form.validate():
        return redirect(url_for('main.explore'))
    page_start = request.args.get('page', 1, type=int)
    page_end = current_app.config['POSTS_PER_PAGE']
    posts, total = Post.search(g.search_form.q.data, page_start, page_end)
    next_url = url_for('main.search', q=g.search_form.q.data, page=page_start + 1) \
        if total > page_start * page_end else None
    prev_url = url_for('main.search', q=g.search_form.q.data, page=page_start - 1) \
        if page_start > 1 else None
    return render_template('search.html', title=_('Search'), posts=posts,
                           next_url=next_url, prev_url=prev_url)


@bp.route('/user/<username>/popup')
@login_required
def user_popup(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user_popup.html', user=user)
