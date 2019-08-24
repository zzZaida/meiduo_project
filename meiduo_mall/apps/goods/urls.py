from django.conf.urls import url
from django.contrib import admin

from . import views

urlpatterns = [

    # 1 商品列表页  /list/(?P<category_id>\d+)/(?P<page_num>\d+)/
    url(r'^list/(?P<category_id>\d+)/(?P<page_num>\d+)/$', views.ListView.as_view(), name='list'),

    # 2 列表页热销排行 hot/(?P<category_id>\d+)/
    url(r'^hot/(?P<category_id>\d+)/$', views.HotGoodsView.as_view()),

    # 3 详情页 /detail/(?P<sku_id>\d+)/
    url(r'^detail/(?P<sku_id>\d+)/$', views.DetailView.as_view(), name='detail'),

]
