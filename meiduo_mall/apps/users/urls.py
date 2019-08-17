
from django.conf.urls import url
from django.contrib import admin

from . import views

urlpatterns = [

    # 1.注册功能
    url(r'^register$', views.RegisterView.as_view()),

    # 2.用户名是否重复  /usernames/(?P<username>[a-zA-Z0-9_-]{5,20})/count/
    url(r'^usernames/(?P<username>[a-zA-Z0-9_-]{5,20})/count/$', views.UsernameCountView.as_view()),

]
