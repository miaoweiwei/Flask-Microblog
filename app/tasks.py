#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2019/7/21 20:04
@Author  : miaoweiwei
@File    : tasks.py
@Software: PyCharm
@Desc    : 后台任务
"""

import time


def example(seconds):
    """该任务将秒数作为参数，然后在该时间量内等待，并每秒打印一次计数器。"""
    print('Starting task')
    for i in range(seconds):
        print(i)
        time.sleep(1)
    print('Task completed')
