from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views import View


class PaymentView(LoginRequiredMixin, View):
    """订单支付功能"""
    def get(self, request, order_id):
        pass
