#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2019/7/19 9:48
@Author  : miaoweiwei
@File    : forms.py
@Software: PyCharm
@Desc    : 
"""
from flask import request
from flask_babel import lazy_gettext as _l
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, ValidationError, Length

from app.models import User


class EditProfileForm(FlaskForm):
    username = StringField(_l('Username'), validators=[DataRequired()])
    about_me = TextAreaField(_l('About me'), validators=[Length(min=0, max=140)])
    submit = SubmitField(_l('Submit'))

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        """验证用户名是否已经存在"""
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError(_l('Please use a different username.'))


class PostForm(FlaskForm):
    """发布用户动态的表单"""
    post = TextAreaField("", validators=[DataRequired(), Length(min=1, max=140)])  # "What's new to tell everyone?"
    submit = SubmitField(_l('Release'))


class SearchForm(FlaskForm):
    q = StringField(_l('Search'), validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        if 'formdata' not in kwargs:
            kwargs['formdata'] = request.args
        if 'csrf_enabled' not in kwargs:
            kwargs['csrf_enabled'] = False
        super(SearchForm, self).__init__(*args, **kwargs)
