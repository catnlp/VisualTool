# -*- coding: utf-8 -*-
# @Author  : catnlp
# @FileName: urls.py
# @Time    : 2020/7/3 21:11

from django.urls import path

from . import views

app_name = 'authorize'
urlpatterns = [
    path('', views.index, name='index'),
]
