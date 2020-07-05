# -*- coding: utf-8 -*-
# @Author  : catnlp
# @FileName: urls.py
# @Time    : 2020/7/3 22:21

from django.urls import path

from . import views

app_name = 'services'
urlpatterns = [
    path('', views.index, name='index'),
    path('upload/', views.upload, name='upload'),
    path('detail/', views.detail, name='detail'),
    path('change/', views.change, name='change'),
]
