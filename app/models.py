#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2019/6/22 13:53
@Author  : miaoweiwei
@File    : models.py
@Software: PyCharm
@Desc    : 数据库模型
"""
import jwt
from datetime import datetime
from time import time
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from hashlib import md5
from app import db, login, current_app
from app.search import remove_from_index, add_to_index, query_index


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


# 监听提交之前和之后的事件,请注意，db.event.listen()调用不在类内部，而是在其后面。 这两行代码设置了每次提交之前和之后调用的事件处理程序。
db.event.listen(db.session, 'before_commit', SearchableMixin.before_commit)
db.event.listen(db.session, 'after_commit', SearchableMixin.after_commit)

#  用户之间的关注 粉丝关系，followers表是关系的关联表
followers = db.Table('followers',
                     db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),  # 关注者
                     db.Column('followed_id', db.Integer, db.ForeignKey('user.id')))  # 被关注者


# 创建的User类继承自db.Model 实际上是一个表，它是Flask-SQLAlchemy中所有模型的基类这个类将表的字段定义为类属性，
# 字段被创建为db.Column类的实例，它传入字段类型以及其他可选参数
class User(UserMixin, db.Model):
    """用户表"""
    id = db.Column(db.Integer, primary_key=True)  # 字段 id ，主键
    username = db.Column(db.String(64), index=True, unique=True)  # unique表示唯一的
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)  # 注意datetime.utcnow不要写成datetime.utcnow()
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')

    # 第一个参数表示右侧实体
    # secondary 指定了用于该关系的关联表，就是使用我在上面定义的followers。
    # primaryjoin 指明了通过关系表关联到左侧实体（关注者）的条件 。关系中的左侧的join条件是关系表中的follower_
    # id字段与这个关注者的用户ID匹配。followers.c.follower_id表达式引用了该关系表中的follower_id列。

    # backref定义了右侧实体如何访问该关系，在左侧，关系被命名为followed，所以在右侧我将使用followers来表示所有左侧用户的列表，即粉丝列表
    # 附加的lazy参数表示这个查询的执行模式，设置为动态模式的查询不会立即执行，直到被调用

    # 用db.relationship初始化。这不是实际的数据库字段，而是用户和其动态之间关系的高级视图，因此它不在数据库图表中,
    # 对于一对多关系，db.relationship字段通常在“一”的这边定义，并用作访问“多”的便捷方式。因此，如果我有一个用户实例u，
    # 表达式u.posts将运行一个数据库查询，返回该用户发表过的所有动态
    # db.relationship的第一个参数表示代表关系“多”的类。 backref参数定义了代表“多”的类的实例反向调用“一”的时候的属性名称。
    # 这将会为用户动态添加一个属性post.author，调用它将返回给该用户动态的用户实例。 lazy参数定义了这种关系调用的数据库查询是如何执行的，

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
