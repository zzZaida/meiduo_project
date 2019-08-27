
from django.conf.urls import url
from django.contrib import admin

from . import views


urlpatterns = [
    # 1.结算订单页面  orders/settlement/
    url(r'^orders/settlement/$', views.OrderSettlementView.as_view(), name='settlement'),

    # 2.提交订单  orders/commit/
    url(r'^orders/commit/$', views.OrderCommitView.as_view(), name='commit')

]
