#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2019/7/20 11:24
@Author  : miaoweiwei
@File    : search.py
@Software: PyCharm
@Desc    : 全文搜索模块
"""
from flask import current_app


def add_to_index(index, model):
    """ 添加索引
    :param index:
    :param model:
    :return:
    """
    if not current_app.elasticsearch:
        return
    payload = {}
    for field in model.__searchable__:
        payload[field] = getattr(model, field)
    current_app.elasticsearch.index(index=index, doc_type=index, id=model.id,
                                    body=payload)


def remove_from_index(index, model):
    if not current_app.elasticsearch:
        return
    current_app.elasticsearch.delete(index=index, doc_type=index, id=model.id)


def query_index(index, query, page, per_page):
    """ 搜索
    :param index:
    :param query: 搜索的内容
    :param page:
    :param per_page:
    :return: 返回两个值：第一个是搜索结果的id元素列表，第二个是结果总数。
    """
    if not current_app.elasticsearch:
        return [], 0
    # es.search()查询的body参数还包含分页参数。 from和size参数控制整个结果集的哪些子集需要被返回
    # Elasticsearch没有像Flask-SQLAlchemy那样提供一个很好的Pagination对象，所以我必须使用分页数学逻辑来计算from值。

    # 如果elasticsearch的python包的版本低于7.0就是用这句
    # search = current_app.elasticsearch.search(
    #     index=index, doc_type=index,
    #     body={'query': {'multi_match': {'query': query, 'fields': ['*']}},
    #           'from': (page - 1) * per_page, 'size': per_page})
    # 高于7.0就是用这句，不同 elasticsearch 服务版本可能返回的json也不一样
    search = current_app.elasticsearch.search(index=index,
                                              body={'query': {'multi_match': {'query': query, 'fields': ['*']}},
                                                    'from': (page - 1) * per_page, 'size': per_page})

    ids = [int(hit['_id']) for hit in search['hits']['hits']]
    return ids, search['hits']['total']['value']

# 以上这些函数都是通过检查app.elasticsearch是否为None开始的，如果是None，则不做任何事情就返回。
# 当Elasticsearch服务器未配置时，应用会在没有搜索功能的状态下继续运行，不会出现任何错误。 这都是为了方便开发或运行单元测试。
