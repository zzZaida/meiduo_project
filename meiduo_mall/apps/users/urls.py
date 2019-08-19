
from django.conf.urls import url
from django.contrib import admin

from . import views

urlpatterns = [

    # 1.注册功能
    url(r'^register$', views.RegisterView.as_view()),

    # 2.用户名是否重复  /usernames/(?P<username>[a-zA-Z0-9_-]{5,20})/count/
    url(r'^usernames/(?P<username>[a-zA-Z0-9_-]{5,20})/count/$', views.UsernameCountView.as_view()),

    # 3.手机号是否重复 /mobiles/(?P<mobile>1[3-9]\d{9})/count/
    url(r'^mobiles/(?P<mobile>1[3-9]\d{9})/count/$', views.MobileCountView.as_view()),

    # 4.登录页 login/
    url(r'^login/$', views.LoginView.as_view(), name='login'),

    # 5 退出 logout/
    url(r'^logout/$', views.LogoutView.as_view()),

    # 6 个人中心 	/info/
    url(r'^info/$', views.UserInfoView.as_view()),

    # 7 邮箱 emails/
    url(r'^emails/$', views.EmailView.as_view()),

]
