
from django.conf.urls import url
from django.contrib import admin

from . import views

# 根路由
urlpatterns = [

    url(r'^$', views.IndexView.as_view(), name='index'),

]
