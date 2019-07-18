#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2019/7/17 11:27
@Author  : miaoweiwei
@File    : translate.py
@Software: PyCharm
@Desc    : 文本翻译
"""
import json
import requests
from flask_babel import _
from app import app


def translate(text, source_language, dest_language):
    """ 翻译函数
    :param text: 要翻译的内容
    :param source_language: 原语言类型
    :param dest_language: 目标语言类型
    :return: 返回翻译的结果
    """
    if 'MS_TRANSLATOR_KEY' not in app.config or not app.config['MS_TRANSLATOR_KEY']:
        return _('Error: the translation service is not  configured.')
    auth = {'Ocp-Apim-Subscription-Key': app.config['MS_TRANSLATOR_KEY']}
    r = requests.get(
        'https://api.microsofttranslator.com/v2/Ajax.svc/Translate?text={}&from={}&to={}'.format(text,
                                                                                                 source_language,
                                                                                                 dest_language),
        headers=auth)
    if r.status_code != 200:
        return _('Error : the translation service failed.')
    return json.loads(r.content.decode('utf-8-sig'))

# https://translate.google.cn/?hl=zh-CN&tab=TT0#view=home&op=translate&sl=auto&tl=zh-CN&text=hello
