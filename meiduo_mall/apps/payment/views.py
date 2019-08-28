import os
from django import http
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views import View
from apps.orders.models import OrderInfo
from alipay import AliPay

from apps.payment.models import Payment
from utils.response_code import RETCODE


class PaymentView(LoginRequiredMixin, View):
    """订单支付功能"""
    def get(self, request, order_id):

        # 1.接收 路径传参(order_id)

        # 2.校验 order 是不是当前的 user; 订单状态是不是未支付
        user = request.user
        try:
            order = OrderInfo.objects.get(user=user, order_id=order_id, status=OrderInfo.ORDER_STATUS_ENUM['UNPAID'])
        except OrderInfo.DoesNotExist:
            return http.HttpResponseForbidden('订单信息错误')

        # 3.和支付宝 建立 链接认证
        """
        ALIPAY_APPID = '2016101400682135'
        ALIPAY_DEBUG = True
        ALIPAY_URL = 'https://openapi.alipaydev.com/gateway.do'
        ALIPAY_RETURN_URL = 'http://www.meiduo.site:8000/payment/status/'
        """
        alipay = AliPay(
            appid=settings.ALIPAY_APPID,
            app_notify_url=None,
            app_private_key_path=os.path.join(os.path.dirname(os.path.abspath(__file__)),'keys/app_private_key.pem'),
            alipay_public_key_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'keys/alipay_public_key.pem'),
            sign_type="RSA2",
            debug=settings.ALIPAY_DEBUG
        )

        # 'https://openapi.alipaydev.com/gateway.do?' + order_string
        # 4.加密我们要给支付宝传递的参数 order_id  total_amount
        order_string = alipay.api_alipay_trade_page_pay(
            subject="美多商城_%s" % order_id,
            out_trade_no=order_id,
            total_amount=str(order.total_amount),
            return_url=settings.ALIPAY_RETURN_URL
        )
        alipay_url = settings.ALIPAY_URL + '?' +order_string

        # 5.返回支付宝的链接 给前端
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'alipay_url': alipay_url})


class PaymentStatusView(View):
    """保存订单支付结果"""
    def get(self, request):
        # 接收参数
        query_params = request.GET.dict()
        # 1.取出签名值
        sign = query_params.pop('sign')

        # 2.认证对象alipay
        alipay = AliPay(
            appid=settings.ALIPAY_APPID,
            app_notify_url=None,
            app_private_key_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'keys/app_private_key.pem'),
            alipay_public_key_path=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                'keys/alipay_public_key.pem'),
            sign_type="RSA2",
            debug=settings.ALIPAY_DEBUG
        )

        # 3.通过校验 入库--支付宝二次校验
        success = alipay.verify(query_params, sign)

        if success:
            Payment.objects.create(
                # 订单id
                order_id=query_params['out_trade_no'],
                # 支付宝交易id
                trade_id=query_params['trade_no']
            )

            context = {
                'trade_id': query_params['trade_no']
            }

            return render(request, 'pay_success.html', context)
        else:
            # 订单支付失败，重定向到我的订单
            return http.HttpResponseForbidden('非法请求')