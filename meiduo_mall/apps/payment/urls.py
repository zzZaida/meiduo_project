
from django.conf.urls import url
from django.contrib import admin

from . import views

urlpatterns = [
    #  支付宝 /payment/(?P<order_id>\d+)/
    url(r'^payment/(?P<order_id>\d+)/$', views.PaymentView.as_view()),

]
