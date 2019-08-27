from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views import View


class OrderSettlementView(LoginRequiredMixin, View):

    def get(self, request):
        """提供订单结算页面"""
        return render(request, 'place_order.html')
