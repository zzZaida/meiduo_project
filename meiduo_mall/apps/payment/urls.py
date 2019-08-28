
from django.conf.urls import url
from django.contrib import admin

from . import views

urlpatterns = [

    #  支付宝链接  payment/(?P<order_id>\d+)/
    url(r'^payment/(?P<order_id>\d+)/$', views.PaymentView.as_view()),

    #  保存订单支付结果  payment/status/
    url(r'^payment/status/$', views.PaymentStatusView.as_view()),

]
