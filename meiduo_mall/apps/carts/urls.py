
from django.conf.urls import url
from django.contrib import admin

from . import views

# 根路由
urlpatterns = [

    # 购物车
    url(r'^carts/$', views.CartsView.as_view()),

]
