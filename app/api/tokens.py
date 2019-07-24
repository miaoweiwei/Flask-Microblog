# -*- coding: utf-8 -*-
"""
@Time    : 2019/7/23 13:55
@Author  : miaoweiwei
@File    : tokens.py
@Software: PyCharm
@Desc    : tokens.py是将要定义认证子系统的模块。 它将为非Web浏览器登录的客户端提供另一种方式。
我在前一节中添加的API endpoint当前对任何客户端都是开放的。 显然，执行这些操作需要认证用户才安全，
为此我需要添加认证和授权，简称“AuthN”和“AuthZ”。 思路是，客户端发送的请求提供了某种标识，
以便服务器知道客户端代表的是哪位用户，并且可以验证是否允许该用户执行请求的操作。
保护这些API endpoint的最明显的方法是使用Flask-Login中的@login_required装饰器，但是这种方法存在一些问题。
装饰器检测到未通过身份验证的用户时，会将用户重定向到HTML登录页面。 在API中没有HTML或登录页面的概念，
如果客户端发送带有无效或缺少凭证的请求，服务器必须拒绝请求并返回401状态码。 服务器不能假定API客户端是Web浏览器，
或者它可以处理重定向，或者它可以渲染和处理HTML登录表单。 当API客户端收到401状态码时，它知道它需要向用户询问凭证，
但是它是如何实现的，服务器不需要关心。
"""
from flask import jsonify, g
from app import db
from app.api import bp
from app.api.auth import basic_auth
from app.api.auth import token_auth

"""
这个视图函数使用了HTTPBasicAuth实例中的@basic_auth.login_required装饰器，
它将指示Flask-HTTPAuth验证身份（通过 auth.verify_password() 验证函数），并且仅当提供的凭证是有效的才运行下面的视图函数。
该视图函数的实现依赖于用户模型的get_token()方法来生成token。 数据库提交在生成token后发出，以确保token及其到期时间被写回到数据库。
 """


@bp.route('/tokens', methods=['POST'])
@basic_auth.login_required
def get_token():
    token = g.current_user.get_token()
    db.session.commit()
    return jsonify({'token': token})


"""
客户端可以向 /tokens URL发送DELETE请求，以使token失效。此路由的身份验证是基于token的，事实上，
在Authorization头部中发送的token就是需要被撤销的。撤销使用了User类中的辅助方法，
该方法重新设置token过期日期来实现撤销操作。之后提交数据库会话，以确保将更改写入数据库。
这个请求的响应没有正文，所以我可以返回一个空字符串。Return语句中的第二个值设置状态代码为204，
该代码用于成功请求却没有响应主体的响应。
下面是撤销token的一个HTTPie请求示例：

(venv) $ http DELETE http://localhost:5000/api/tokens  Authorization:"Bearer pC1Nu9wwyNt8VCj1trWilFdFI276AcbS"
"""


@bp.route('/tokens', methods=['DELETE'])
@token_auth.login_required
def revoke_token():
    g.current_user.revoke_token()
    db.session.commit()
    return '', 204
