#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2019/6/29 20:44
@Author  : miaoweiwei
@File    : cli.py
@Software: PyCharm
@Desc    : 翻译和本地化自定义命令
"""
import os
import click


def register(app):
    # Flask依赖Click进行所有命令行操作。 像translate这样的命令是几个子命令的根，
    # 它们是通过app.cli.group()装饰器创建的。 我将把这些命令放在一个名为app/cli.py的新模块中：
    @app.cli.group()
    def translate():
        """翻译和本地化命令"""
        pass
        # 该命令的名称来自被装饰函数的名称，并且帮助消息来自文档字符串。
        # 由于这是一个父命令，它的存在只为子命令提供基础，函数本身不需要执行任何操作。

    @translate.command()
    def update():
        """用于更新所有语言存储库"""
        if os.system('pybabel extract -F babel.cfg -k _l -o messages.pot .'):
            raise RuntimeError('extract command failed')
        if os.system('pybabel update -i messages.pot -d app/translations'):
            raise RuntimeError('update command failed')
        os.remove('messages.pot')

    @translate.command()
    def complete():
        """用于编译所有语言存储库"""
        if os.system('pybabel compile -d app/translations'):
            raise RuntimeError('compile command failed')

    @translate.command()
    @click.argument('lang')
    def init(lang):
        """初始化一种新语言。"""
        if os.system('pybabel extract -F babel.cfg -k _l -o messages.pot .'):
            raise RuntimeError('extract command failed')
        if os.system(
                'pybabel init -i messages.pot -d app/translations -l ' + lang):
            raise RuntimeError('init command failed')
        os.remove('messages.pot')
