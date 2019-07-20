#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2019/6/19 22:23
@Author  : miaoweiwei
@File    : run.py
@Software: PyCharm
@Desc    :这个脚本简单地从我们的 app 包中导入 app 变量并且调用它的 run 方法来启动服务器。
请记住 app 变量中含有我们在之前创建的 Flask 实例。
要启动应用程序，您只需运行此脚本（run.py）
在服务器初始化后，它将会监听 5000 端口等待着连接。现在打开你的网页浏览器输入如下 URL:
http://localhost:5000
另外你也可以使用这个 URL:
http://localhost:5000/index
"""
from app import create_app, db, cli
from app.models import User, Post

app = create_app()  # 调用工程函数
cli.register(app)  # 注册语言翻译的快捷命令


# 它通过添加数据库实例和模型来创建了一个shell上下文环境
# app.shell_context_processor装饰器将该函数注册为一个shell上下文函数。
# 当flask shell命令运行时，它会调用这个函数并在shell会话中注册它返回的项目。
# 函数返回一个字典而不是一个列表，原因是对于每个项目，你必须通过字典的键提供一个名称以便在shell中被调用。


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Post': Post}


print("run.py服务启动了")

if __name__ == '__main__':
    # debug=True 会使在运行时若代码改动则会使项目重新启动，但这会使项目第一次启动时重启一次
    # app.run()
    app.run(host='0.0.0.0', port=5000, debug=True)
