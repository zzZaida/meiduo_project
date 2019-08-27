from django.conf.urls import url
from django.contrib import admin

from . import views

urlpatterns = [

    # 购物车
    url(r'^carts/$', views.CartsView.as_view()),

    # 全选 /carts/selection/
    url(r'^carts/selection/$', views.CartsSelectAllView.as_view()),

    # 展示商品页面简单购物车 carts/simple/
    url(r'^carts/simple/$', views.CartsSimpleView.as_view()),

]
