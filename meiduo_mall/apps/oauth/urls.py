
from django.conf.urls import url
from django.contrib import admin

from . import views

urlpatterns = [

    url(r'^qq/login/$', views.QQAuthURLView.as_view(), name='QQ'),

]
