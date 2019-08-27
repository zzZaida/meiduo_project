
from django.conf.urls import url
from django.contrib import admin

from . import views


urlpatterns = [
    # 结算订单页面  orders/settlement/
    url(r'^orders/settlement/$', views.OrderSettlementView.as_view(), name='settlement'),

]
