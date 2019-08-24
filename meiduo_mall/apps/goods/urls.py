
from django.conf.urls import url
from django.contrib import admin

from . import views

# 商品列表页  /list/(?P<category_id>\d+)/(?P<page_num>\d+)/
urlpatterns = [

    url(r'^/list/(?P<category_id>\d+)/(?P<page_num>\d+)/$', views.ListView.as_view(), name='list'),

]
