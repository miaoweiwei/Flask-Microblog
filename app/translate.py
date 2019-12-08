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
import random
from hashlib import md5
from flask_babel import _
from guess_language import guess_language
from app import current_app


def identify_language(text, baidu=True):
    """ 识别语言的类型
    @param text:要识别语言类型的字符串
    @param baidu:是否使用百度api去识别，不使用百度的api就使用 guess_language 这个python包
    @return:返回识别结果，就是语言的类型
    """
    if not baidu:
        return guess_language(text)  # 使用识别语言类型的包
    url = 'https://fanyi.baidu.com/langdetect?query=' + text
    r = requests.get(url)
    if r.status_code != 200:
        print(_('Error : the identify language service failed.'))
        return ""
    text = r.content.decode('utf-8-sig')
    text = json.loads(text)
    if text['msg'] == 'success':
        return text['lan']
    return ''


def ms_translate(text, source_language, dest_language):
    """ 微软的翻译接口函数
    :param text: 要翻译的内容
    :param source_language: 原语言类型
    :param dest_language: 目标语言类型
    :return: 返回翻译的结果
    """
    if 'MS_TRANSLATOR_KEY' not in current_app.config or not current_app.config['MS_TRANSLATOR_KEY']:
        return _('Error: the translation service is not  configured.')
    auth = {'Ocp-Apim-Subscription-Key': current_app.config['MS_TRANSLATOR_KEY']}
    r = requests.get(
        'https://api.microsofttranslator.com/v2/Ajax.svc/Translate?text={}&from={}&to={}'.format(text, source_language,
                                                                                                 dest_language),
        headers=auth)
    if r.status_code != 200:
        return _('Error : the translation service failed.')
    text = r.content.decode('utf-8-sig')
    return json.loads(text)


def baidu_translate(q, source_language, dest_language):
    """ 百度翻译
    :param q: 要翻译的内容
    :param source_language: 原语言类型
    :param dest_language: 目标语言类型
    :return: 返回翻译结果
    """
    if ('BAIDU_TRANSLATE_APPID' not in current_app.config or not current_app.config['BAIDU_TRANSLATE_APPID']) and \
            ('BAIDU_TRANSLATE_SECRET' not in current_app.config or not current_app.config['BAIDU_TRANSLATE_SECRET']):
        return _('Error: the translation service is not  configured.')
    if source_language is None:
        source_language = 'auto'  # 语言种类未知就传auto
    appid = current_app.config['BAIDU_TRANSLATE_APPID']
    secret_key = current_app.config["BAIDU_TRANSLATE_SECRET"]
    salt = random.randint(32768, 65536)
    temp_str = appid + q + str(salt) + secret_key
    sign = md5(temp_str.encode('utf-8')).hexdigest()
    url = 'http://api.fanyi.baidu.com/api/trans/vip/translate?q={}&from={}&to={}&appid={}&salt={}&sign={}'.format(q,
                                                                                                                  source_language,
                                                                                                                  dest_language,
                                                                                                                  appid,
                                                                                                                  str(
                                                                                                                      salt),
                                                                                                                  sign)
    r = requests.get(url)
    if r.status_code != 200:
        return _('Error : the translation service failed.')
    text = json.loads(r.content.decode('utf-8'))
    text = text['trans_result'][0]['dst']
    return text
