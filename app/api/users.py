#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2019/7/23 12:20
@Author  : miaoweiwei
@File    : users.py
@Software: PyCharm
@Desc    : 跟用户有关的api,用户API资源占位符。

HTTP 方法	资源 URL	                注释
GET         /api/users/<id>	            返回一个用户
GET	        /api/users	                返回所有用户的集合
GET	        /api/users/<id>/followers	返回某个用户的粉丝集合
GET	        /api/users/<id>/followed	返回某个用户关注的用户集合
POST	    /api/users	                注册一个新用户
PUT	        /api/users/<id>	            修改某个用户
"""
from app import db
from app.api import bp
from app.api.errors import bad_request
from app.api.auth import token_auth
from app.models import User
from flask import jsonify, request, url_for

"""为了使用token保护API路由，需要添加@token_auth.login_required装饰器："""


@bp.route('/users/<int:id>', methods=['GET'])
@token_auth.login_required
def get_user(id):
    return jsonify(User.query.get_or_404(id).to_dict())


@bp.route('/users', methods=['GET'])
@token_auth.login_required
def get_users():
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    data = User.to_collection_dict(User.query, page, per_page, 'api.get_users')
    return jsonify(data)


@bp.route('/users/<int:id>/followers', methods=['GET'])
@token_auth.login_required
def get_followers(id):
    user = User.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    data = User.to_collection_dict(user.followers, page, per_page,
                                   'api.get_followers', id=id)
    return jsonify(data)


@bp.route('/users/<int:id>/followed', methods=['GET'])
@token_auth.login_required
def get_followed(id):
    user = User.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    data = User.to_collection_dict(user.followed, page, per_page,
                                   'api.get_followed', id=id)
    return jsonify(data)


@bp.route('/users', methods=['POST'])
def create_user():
    """注册新用户"""
    # Flask提供request.get_json()方法从请求中提取JSON并将其作为Python结构返回。 如果在请求中没有找到JSON数据，该方法返回None
    data = request.get_json() or {}
    if 'username' not in data or 'email' not in data or 'password' not in data:
        return bad_request('must include username, email and password fields')
    if User.query.filter_by(username=data['username']).first():
        return bad_request('please use a different username')
    if User.query.filter_by(email=data['email']).first():
        return bad_request('please use a different email address')
    user = User()
    user.from_dict(data, new_user=True)
    db.session.add(user)
    db.session.commit()
    response = jsonify(user.to_dict())
    response.status_code = 201
    response.headers['Location'] = url_for('api.get_user', id=user.id)
    return response


@bp.route('/users/<int:id>', methods=['PUT'])
@token_auth.login_required
def update_user(id):
    """编辑用户api"""
    user = User.query.get_or_404(id)
    data = request.get_json() or {}
    # 判断客户端传来的信息里 是否有用户名 用户名是否和原来的一样 若不一样则这个新的用户名是否和数据库里的其他用户的用户名一样
    if 'username' in data and data['username'] != user.username and \
            User.query.filter_by(username=data['username']).first():
        return bad_request('please use a different username')
    if 'email' in data and data['email'] != user.email and User.query.filter_by(email=data['email']).first():
        return bad_request('please use a different email address')
    user.from_dict(data, new_user=False)
    db.session.commit()
    return jsonify(user.to_dict())


"""
如果你直接对上面列出的受token保护的endpoint发起请求，则会得到一个401错误。为了成功访问，你需要添加Authorization头部，
其值是请求 /api/tokens 获得的token的值。Flask-HTTPAuth期望的是"不记名"token，但是它没有被HTTPie直接支持。就像针对基本认证，
HTTPie提供了--auth选项来接受用户名和密码，但是token的头部则需要显式地提供了。下面是发送不记名token的格式：

(venv) $ http GET http://localhost:5000/api/users/1 Authorization:"Bearer pC1Nu9wwyNt8VCj1trWilFdFI276AcbS"
pC1Nu9wwyNt8VCj1trWilFdFI276AcbS是用户的token

可以先使用 http --auth miao:123456 POST http://localhost:5000/api/tokens 获取token
返回结果为
HTTP/1.0 200 OK
Content-Length: 50
Content-Type: application/json
Date: Wed, 24 Jul 2019 02:32:42 GMT
Server: Werkzeug/0.15.5 Python/3.7.0

{
    "token": "0rG+SAbpuS3PeOZn1dz/7Ly0IFXB0mu5"
}

然后在使用这个token去访问其他的api如上面的用户信息api
(venv) $ http GET http://localhost:5000/api/users/1 Authorization:"Bearer 0rG+SAbpuS3PeOZn1dz/7Ly0IFXB0mu5" 
返回
HTTP/1.0 200 OK
Content-Length: 440
Content-Type: application/json
Date: Wed, 24 Jul 2019 02:34:38 GMT
Server: Werkzeug/0.15.5 Python/3.7.0

{
    "_links": {
        "avatar": "https://www.gravatar.com/avatar/e4a46b9d6cd18dc255e04681f1ec2e61?d=identicon&s=128",
        "followed": "/api/users/1/followed",
        "followers": "/api/users/1/followers",
        "self": "/api/users/1"
    },
    "about_me": "我是第一个用户",
    "followed_count": 0,
    "follower_count": 0,
    "id": 1,
    "last_seen": "2019-07-22T15:12:50Z",
    "post_count": 2,
    "username": "miao"
}
"""
