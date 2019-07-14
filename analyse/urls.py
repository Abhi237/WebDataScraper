# -*- coding: utf-8 -*-
"""
Created on Tue Jun 25 23:23:41 2019

@author: Abhishek
"""

from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="analyse-home"),
    path('result/', views.result, name="analyse-result"),
    path('reviews/',views.reviews,name="analyse-review"),
    path('sentiment/',views.sentiment,name="analyse-sentiment")
]
