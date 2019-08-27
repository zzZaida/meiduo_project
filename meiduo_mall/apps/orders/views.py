import json

from decimal import Decimal
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views import View
from django_redis import get_redis_connection

from apps.areas.models import Address
from apps.goods.models import SKU


class OrderSettlementView(LoginRequiredMixin, View):

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
