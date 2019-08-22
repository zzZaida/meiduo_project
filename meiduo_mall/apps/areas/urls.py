
from django.conf.urls import url
from django.contrib import admin

from . import views

# 查询省市区数据  areas/
urlpatterns = [

    url(r'^areas/$', views.AreasView.as_view()),

]
