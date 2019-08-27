import json
from datetime import datetime

from decimal import Decimal

from django import http
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views import View
from django_redis import get_redis_connection

from apps.areas.models import Address
from apps.goods.models import SKU
from apps.orders.models import OrderInfo


class OrderSettlementView(LoginRequiredMixin, View):
    """结算订单"""
    def get(self, request):
        """提供订单结算页面"""

        # 获取登录用户
        user = request.user
        # 1.查询地址
        try:
            addresses = Address.objects.filter(user=user, is_deleted=False)
        except Exception as e:
            #  如果地址为空，渲染模板时会判断，并跳转到地址编辑页面
            addresses = None

        # 2.取redis数据  购物车数据-选中的商品
        redis_client = get_redis_connection('carts')
        carts_data = redis_client.hgetall(user.id)
        # 遍历选中的商品
        carts_dict = {}
        for key,value in carts_data.items():
            sku_id = int(key.decode())
            sku_dict = json.loads(value.decode())

            if sku_dict['selected']:
                carts_dict[sku_id] = sku_dict

        # 3.选中的商品id->SKU商品
        skus = SKU.objects.filter(id__in=carts_dict.keys())

        # 计算总个数 和 总金额
        total_count = 0
        total_amount = Decimal(0.00)
        for sku in skus:
            # 动态添加 count 和 amount 属性
            sku.count = carts_dict[sku.id]['count']
            sku.amount = sku.count * sku.price

            # 计算总个数 和 总金额
            total_count += sku.count
            total_amount += sku.amount

        # 运费
        freight = Decimal('10.00')

        # 4.构建前端需要的数据格式
        context = {
            'addresses': addresses,
            'skus': skus,
            'total_count': total_count,
            'total_amount': total_amount,
            'freight': freight,
            'payment_amount': total_amount + freight,
            'default_address_id': user.default_address_id
        }
        return render(request, 'place_order.html', context)


class OrderCommitView(LoginRequiredMixin, View):
    """订单提交"""

    def post(self, request):
        """保存订单信息和订单商品信息"""

        # 1.接收参数  地址 支付方式 json传参
        json_dict = json.loads(request.body.decode())
        address_id = json_dict.get('address_id')
        pay_method = json_dict.get('pay_method')

        # 2.校验 地址存在吗, 支付方式 我们有没有
        if not all([address_id, pay_method]):
            return http.HttpResponseForbidden('缺少必传参数')
        try:
            address = Address.objects.get(id=address_id)
        except Exception as e:
            return http.HttpResponseForbidden('参数address_id错误')

        if pay_method not in [OrderInfo.PAY_METHODS_ENUM['CASH'], OrderInfo.PAY_METHODS_ENUM['ALIPAY']]:
            return http.HttpResponseForbidden('参数pay_method错误')

        # 3.生成订单号-->订单单表数据-->订单商品表
        # 3.1 生成订单号:时间+用户id
        user = request.user
        order_id = datetime.now().strftime('%Y%m%d%H%M%S') + ('%09d' % user.id)

        # 3.2 订单表数据
        order = OrderInfo.objects.create(
            order_id=order_id,
            user=user,
            address=address,
            total_count=0,
            total_amount=Decimal('0'),
            freight=Decimal('10.00'),
            pay_method=pay_method,
            status=OrderInfo.ORDER_STATUS_ENUM['UNPAID'] if pay_method == OrderInfo.PAY_METHODS_ENUM['ALIPAY'] else
            OrderInfo.ORDER_STATUS_ENUM['UNSEND']
        )
        # 如果 购买个数 大于 库存stock

        # 4.SKU 销量增加 库存减少

        # 5.SPU 销量增加

        # 重新计算 购买的总个数  总金额  运费

        # 6.清空购物车  已经购买的数据 以前选中的数据

        # 7.返回响应对象