
from django.conf.urls import url
from django.contrib import admin

from . import views

urlpatterns = [

    url(r'^qq/login/$', views.QQAuthURLView.as_view(), name='QQ'),

    # 接收 QQ 返回来的 code
    url(r'^oauth_callback/$', views.QQAuthUserView.as_view()),

]
