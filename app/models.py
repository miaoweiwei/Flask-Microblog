#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2019/6/22 13:53
@Author  : miaoweiwei
@File    : models.py
@Software: PyCharm
@Desc    : 数据库模型
"""
import base64
import json
import os
from datetime import datetime, timedelta
from hashlib import md5
from time import time

import jwt
from flask import current_app, url_for
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login
from app.search import add_to_index, remove_from_index, query_index


class SearchableMixin(object):
    # classmethod 类方法像高级语言的静态方法
    # classmethod类方法 修饰符对应的函数不需要实例化，不需要 self 参数，但第一个参数需要是表示自身类的 cls 参数，可以来调用类的属性，类的方法，实例化对象等。
    @classmethod
    def search(cls, expression, page, per_page):
        """获取搜索结果列表"""
        ids, total = query_index(cls.__tablename__, expression, page, per_page)
        if total == 0:
            return cls.query.filter_by(id=0), 0
        when = []
        for i in range(len(ids)):
            when.append((ids[i], i))
        return cls.query.filter(cls.id.in_(ids)).order_by(db.case(when, value=cls.id)), total  # SQL 的case when语句

    @classmethod
    def before_commit(cls, session):  # 在事务提交发生之前
        session._changes = {
            'add': list(session.new),
            'update': list(session.dirty),
            'delete': list(session.deleted)
        }

    @classmethod
    def after_commit(cls, session):  # 在事务提交发生之后
        # session对象具有before_commit()中添加的_changes变量，所以现在我可以迭代需要被添加，修改和删除的对象，并对app/search.py中的索引函数进行相应的调用。
        for obj in session._changes['add']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['update']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['delete']:
            if isinstance(obj, SearchableMixin):
                remove_from_index(obj.__tablename__, obj)
        session._changes = None

    @classmethod
    def reindex(cls):
        # reindex()类方法是一个简单的帮助方法，你可以使用它来刷新所有数据的索引。
        # 有了这个方法，我可以调用Post.reindex()将数据库中的所有用户动态添加到搜索索引中
        for obj in cls.query:
            add_to_index(cls.__tablename__, obj)


class PaginatedAPIMixin(object):
    """用于分页"""

    @staticmethod
    def to_collection_dict(query, page, per_page, endpoint, **kwargs):
        """产生一个带有用户集合表示的字典
        :param query: Flask-SQLAlchemy查询对象
        :param page: 页码
        :param per_page: 每页数据数量
        :param endpoint: 在endpoint参数中传递的值，来确定需要发送到url_for()的视图函数
        :param kwargs: 视图函数的参数
        :return:
        """
        """
        items是用户资源的列表，
        _meta部分包含集合的元数据，客户端在向用户渲染分页控件时就会用得上
        _links部分定义了相关链接，包括集合本身的链接以及上一页和下一页链接，也能帮助客户端对列表进行分页。
        """
        #  该实现使用查询对象的paginate()方法来获取该页的条目，就像我对主页，发现页和个人主页中的用户动态所做的一样。
        resources = query.paginate(page, per_page, False)
        data = {
            'items': [item.to_dict() for item in resources.items],
            '_meta': {
                'page': page,
                'per_page': per_page,
                'total_pages': resources.pages,
                'total_items': resources.total
            },
            '_links': {
                'self': url_for(endpoint, page=page, per_page=per_page, **kwargs),
                'next': url_for(endpoint, page=page + 1, per_page=per_page, **kwargs) if resources.has_next else None,
                'prev': url_for(endpoint, page=page - 1, per_page=per_page, **kwargs) if resources.has_prev else None
            }
        }
        """复杂的部分是生成链接，其中包括自引用以及指向下一页和上一页的链接。 我想让这个函数具有通用性，
        所以我不能使用类似url_for('api.get_users', id=id, page=page)这样的代码来生成自链接
        （译者注：因为这样就固定成用户资源专用了）。 url_for()的参数将取决于特定的资源集合，
        所以我将依赖于调用者在endpoint参数中传递的值，来确定需要发送到url_for()的视图函数。 
        由于许多路由都需要参数，我还需要在kwargs中捕获更多关键字参数，并将它们传递给url_for()。
         page和per_page查询字符串参数是明确给出的，因为它们控制所有API路由的分页。
         """
        return data


# 监听提交之前和之后的事件,请注意，db.event.listen()调用不在类内部，而是在其后面。 这两行代码设置了每次提交之前和之后调用的事件处理程序。
db.event.listen(db.session, 'before_commit', SearchableMixin.before_commit)
db.event.listen(db.session, 'after_commit', SearchableMixin.after_commit)

#  用户之间的关注 粉丝关系，followers表是关系的关联表
followers = db.Table('followers',
                     db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),  # 关注者
                     db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))  # 被关注者
                     )


# 创建的User类继承自db.Model 实际上是一个表，它是Flask-SQLAlchemy中所有模型的基类这个类将表的字段定义为类属性，
# 字段被创建为db.Column类的实例，它传入字段类型以及其他可选参数
class User(PaginatedAPIMixin, UserMixin, db.Model):
    """用户表"""
    id = db.Column(db.Integer, primary_key=True)  # 字段 id ，主键
    username = db.Column(db.String(64), index=True, unique=True)  # unique表示唯一的
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)  # 注意datetime.utcnow不要写成datetime.utcnow()
    token = db.Column(db.String(32), index=True, unique=True)  # 需要通过它搜索数据库，所以我为它设置了唯一性和索引
    token_expiration = db.Column(db.DateTime)  # 保存token过期的日期和时间。 这使得token不会长时间有效，以免成为安全风险。
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    # 第一个参数表示右侧实体
    # secondary 指定了用于该关系的关联表，就是使用我在上面定义的followers。
    # primaryjoin 指明了通过关系表关联到左侧实体（关注者）的条件 。关系中的左侧的join条件是关系表中的follower_
    # id字段与这个关注者的用户ID匹配。followers.c.follower_id表达式引用了该关系表中的follower_id列。

    # backref定义了右侧实体如何访问该关系，在左侧，关系被命名为followed，所以在右侧我将使用followers来表示所有左侧用户的列表，即粉丝列表
    # 附加的lazy参数表示这个查询的执行模式，设置为动态模式(懒加载)的查询不会立即执行，直到被调用

    # 用db.relationship初始化。这不是实际的数据库字段，而是用户和其动态之间关系的高级视图，因此它不在数据库图表中,
    # 对于一对多关系，db.relationship字段通常在“一”的这边定义，并用作访问“多”的便捷方式。因此，如果我有一个用户实例u，
    # 表达式u.posts将运行一个数据库查询，返回该用户发表过的所有动态
    # db.relationship的第一个参数表示代表关系“多”的类。 backref参数定义了代表“多”的类的实例反向调用“一”的时候的属性名称。
    # 这将会为用户动态添加一个属性post.author，调用它将返回给该用户动态的用户实例。 lazy参数定义了这种关系调用的数据库查询是如何执行的，

    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')
    # Message一侧将添加author和recipient回调引用。 我之所以使用author回调而不是更适合的sender，
    # 是因为通过使用author，我可以使用我用于用户动态的相同逻辑渲染这些消息
    messages_sent = db.relationship('Message',
                                    foreign_keys='Message.sender_id',
                                    backref='author',
                                    lazy='dynamic')
    messages_received = db.relationship('Message',
                                        foreign_keys='Message.recipient_id',
                                        backref='recipient',
                                        lazy='dynamic')
    # last_message_read_time字段将存储用户最后一次访问消息页面的时间，并将用于确定是否有比此字段更新时间戳的未读消息
    last_message_read_time = db.Column(db.DateTime)
    # 通知将会有一个名称，一个关联的用户，一个Unix时间戳和一个有效载荷。
    notifications = db.relationship('Notification', backref='user',
                                    lazy='dynamic')

    # __repr__方法用于在调试时打印用户实例,在下面的Python交互式会话中你可以看到__repr__()方法的运行情况：
    #
    # >>> from app.models import User
    # >>> u = User(username='susan', email='susan@example.com')
    # >>> u
    # <User susan>
    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        """设置密码"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """验证密码是否正确"""
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        """用户头像，对于没有注册头像的用户，将生成“identicon”类的随机图片
        :param size:需求头像的像素大小
        :return:返回用户头像图片的URL
        """
        # 为了生成MD5哈希值，我首先将电子邮件转换为小写，因为这是Gravatar服务所要求的。
        # 然后，因为Python中的MD5的参数类型需要是字节而不是字符串，所以在将字符串传递给该函数之前，需要将字符串编码为字节。
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()  # md5(b'miao@email.com').hexdigest()获取字符串的md5值
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(digest, size)

    # 感谢SQLAlchemy ORM，一个用户关注另一个用户的行为可以通过followed关系抽象成一个列表来简便使用。
    # 例如，如果我有两个用户存储在user1和user2变量中，我可以用下面这个简单的语句来实现：
    def follow(self, user):
        """关注一个用户"""
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        """取消关注"""
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        """"查看该用户是否已经被关注"""
        # filter()它可以包含任意的过滤条件
        # filter_by()只能检查是否等于一个常量值
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0

    def followed_posts(self):
        """查询自己关注的人的博客和自己的博客并按博客的产生时间排序"""
        followed = Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)).filter(
            followers.c.follower_id == self.id)  # 自己关注的人的博客
        own = Post.query.filter_by(user_id=self.id)  # 自己的博客
        return followed.union(own).order_by(Post.timestamp.desc())

        #  join()联合查询，把关系表followers和博客表Posts组成一个新的临时表，
        #  把followers.c.followed_id == Post.user_id的组成一行
        #  filter() 从新的表中选出followers.c.follower_id == self.id的行
        #  Post.timestamp.desc()使用用户动态产生的时间戳按降序排列结果列表

    def get_reset_password_token(self, expire_in=600):
        """以字符串形式生成一个JWT令牌"""
        # 我要用于密码重置令牌的有效载荷格式为{'reset_password'：user_id，'exp'：token_expiration}
        # reset_password字段值为用户id
        # exp字段是JWTs的标准，如果它存在，则表示令牌的到期时间，令牌的有效时间默认为10分钟
        # jwt.encode()返回的是一个字节序列所以要用decode('utf-8')解码成字符串
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expire_in},
            current_app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        """令牌验证"""
        # 尝试通过调用PyJWT的jwt.decode()函数来解码它。
        # 如果令牌不能被验证或已过期，将会引发异常
        try:
            secret_key = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            user_id = secret_key['reset_password']
            exp = secret_key['exp']
        except:
            return
        return User.query.get(user_id)

    def new_messages(self):
        """该方法实际上使用这个字段来返回用户有多少条未读消息。"""
        last_read_time = self.last_message_read_time or datetime(1900, 1, 1)
        return Message.query.filter_by(recipient=self).filter(
            Message.timestamp > last_read_time).count()

    # 此方法不仅为用户添加通知给数据库，还确保如果具有相同名称的通知已存在，则会首先删除该通知
    # 我将要使用的通知将被称为 unread_message_count。 如果数据库已经有一个带有这个名称的通知，
    # 例如值为3，则当用户收到新消息并且消息计数变为4时，我就会替换旧的通知。
    # # 这里的 name 不是人的名字，是指消息个数的代称
    def add_notification(self, name, data):
        self.notifications.filter_by(name=name).delete()
        n = Notification(name=name, payload_json=json.dumps(data), user=self)
        db.session.add(n)
        return n

    def to_dict(self, include_email=False):
        """ 该方法相当于序列化，该方法返回一个Python字典:表示User模型
        :param include_email:email字段需要特殊处理，因为我只想在用户请求自己的数据时才包含电子邮件。
        :return:
        """
        data = {
            'id': self.id,
            'username': self.username,
            'last_seen': self.last_seen.isoformat() + 'Z',
            'about_me': self.about_me,
            'post_count': self.posts.count(),
            'follower_count': self.followers.count(),
            'followed_count': self.followed.count(),
            '_links': {
                'self': url_for('api.get_user', id=self.id),
                'followers': url_for('api.get_followers', id=self.id),
                'followed': url_for('api.get_followed', id=self.id),
                'avatar': self.avatar(128)  # 头像链接是特殊的，因为它是应用外部的Gravatar URL
            }
        }
        """
        注意一下last_seen字段的生成。 对于日期和时间字段，我将使用ISO 8601格式，
        Python的datetime对象可以通过isoformat()方法生成这样格式的字符串。 
        但是因为我使用的datetime对象的时区是UTC，且但没有在其状态中记录时区，
        所以我需要在末尾添加Z，即ISO 8601的UTC时区代码。
        """
        if include_email:
            data['email'] = self.email
        return data

    def from_dict(self, data, new_user=False):
        """ 该函数相当于反序列化，实现从Python字典到User对象的转换
        :param data:
        :param new_user:
        """
        for field in ['username', 'email', 'about_me']:
            if field in data:  # 对于每个字段，我检查它是否存在于data参数中
                setattr(self, field, data[field])  # 使用Python的setattr()在对象的相应属性中设置新值
        # password字段被视为特例，因为它不是对象中的字段。 new_user参数确定了这是否是新的用户注册，
        # 这意味着data中包含password。 要在用户模型中设置密码，需要调用set_password()方法来创建密码哈希。
        if new_user and 'password' in data:
            self.set_password(data['password'])

    def get_token(self, expires_in=3600):
        """ 为用户返回一个token
        :param expires_in: token 有效时间
        :return:
        """
        now = datetime.utcnow()
        # 在创建新token之前，此方法会检查当前分配的token在到期之前是否至少还剩一分钟，并且在这种情况下会返回现有的token。
        if self.token and self.token_expiration > now + timedelta(seconds=60):
            return self.token
        # 以base64编码的24位随机字符串来生成这个token，以便所有字符都处于可读字符串范围内
        self.token = base64.b64encode(os.urandom(24)).decode('utf-8')
        self.token_expiration = now + timedelta(seconds=expires_in)
        db.session.add(self)
        return self.token

    def revoke_token(self):
        """使用token时，有一个策略可以立即使token失效总是一件好事，而不是仅依赖到期日期。 这是一个经常被忽视的安全最佳实践。
            revoke_token()方法使得当前分配给用户的token失效，只需设置到期时间为当前时间的前一秒。
        """
        self.token_expiration = datetime.utcnow() - timedelta(seconds=1)

    @staticmethod
    def check_token(token):
        """ check_token()方法是一个静态方法，它将一个token作为参数传入并返回此token所属的用户。 如果token无效或过期，则该方法返回None。
        :param token:
        :return:
        """
        user = User.query.filter_by(token=token).first()
        if user is None or user.token_expiration < datetime.utcnow():  # 检查是否过期
            return None
        return user


# 插件期望应用配置一个用户加载函数，可以调用该函数来加载给定ID的用户
# 使用Flask-Login的@login.user_loader装饰器来为用户加载功能注册函数。 Flask-Login将字符串类型的参数id传入用户加载函数，
# 因此使用数字ID的数据库需要如上所示地将字符串转换为整数。
@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Post(SearchableMixin, db.Model):
    """用户发表的动态"""
    __searchable__ = ['body']  # 这个模型需要有body字段才能被索引,我添加的这个__searchable__属性只是一个变量，它没有任何关联的行为。 它只会帮助我以通用的方式编写索引函数。
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    # 添加了一个default参数，并传入了datetime.utcnow函数。 当你将一个函数作为默认值传入后，
    # SQLAlchemy会将该字段设置为调用该函数的值（请注意，在utcnow之后我没有包含()，所以我传递函数本身，而不是调用它的结果）。
    # 通常，在服务应用中使用UTC日期和时间是推荐做法。 这可以确保你使用统一的时间戳，无论用户位于何处，这些时间戳会在显示时转换为用户的当地时间。
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # 初始化为user.id的外键,Flask-SQLAlchemy自动设置类名为小写来作为对应表的名称
    language = db.Column(db.String(5))  # 用户发表的动态的语言类型

    def __repr__(self):
        return '<Post {}>'.format(self.body)


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    body = db.Column(db.String(140))
    # 用于指示用户最后一次阅读他们的私有消息的时间
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)  # 这里的utcnow不加括号

    def __repr__(self):
        return '<Message {}>'.format(self.body)


class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    timestamp = db.Column(db.Float, index=True, default=time)
    payload_json = db.Column(db.Text)

    def get_data(self):
        return json.loads(str(self.payload_json))
