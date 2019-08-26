from django.conf.urls import url
from django.contrib import admin

from . import views

urlpatterns = [

    # 购物车
    url(r'^carts/$', views.CartsView.as_view()),

    # 全选 /carts/selection/
    url(r'^carts/selection/$', views.CartsSelectAllView.as_view()),

]
