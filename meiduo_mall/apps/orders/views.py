import json
import time
from datetime import datetime
from decimal import Decimal

from django import http
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views import View
from django_redis import get_redis_connection

from apps.areas.models import Address
from apps.goods.models import SKU
from apps.orders.models import OrderInfo, OrderGoods
from utils.response_code import RETCODE


class OrderSuccessView(LoginRequiredMixin, View):
    """提交订单成功"""
    def get(self, request):
        # 1.接收查询参数
        # http://www.meiduo.site:8000/orders/success/
        # ?order_id=20190827124712000000001&payment_amount=3398&pay_method=2
        order_id = request.GET.get('order_id')
        payment_amount = request.GET.get('payment_amount')
        pay_method = request.GET.get('pay_method')

        # 2.返回前端
        context = {
            'order_id': order_id,
            'payment_amount': payment_amount,
            'pay_method': pay_method
        }
        return render(request, 'order_success.html', context)


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

        from django.db import transaction
        # <1> 开启事务
        with transaction.atomic():
            # <2> 生成 保存点
            save_id = transaction.savepoint()

            # 3.生成订单号-->订单单表数据-->订单商品表
            # 3.1 生成订单号:时间+用户id
            user = request.user
            order_id = datetime.now().strftime('%Y%m%d%H%M%S') + ('%09d' % user.id)

            try:
                # 3.2 订单表数据  <第一张表>OrderInfo
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

                # 3.3 查询购物车redis--已选中的商品
                redis_client = get_redis_connection('carts')
                client_data = redis_client.hgetall(user.id)

                # 筛选选中的商品
                carts_dict = {}
                for key, value in client_data.items():
                    sku_id = int(key.decode())
                    sku_dict = json.loads(value.decode())

                    if sku_dict['selected']:
                        carts_dict[sku_id] = sku_dict

                # 获取所有 选中商品 购买; 商品ids  <两张表>(SKU, SPU)
                sku_ids = carts_dict.keys()
                for sku_id in sku_ids:
                    while True:
                        sku = SKU.objects.get(id=sku_id)
                        # 老库存
                        old_stock = sku.stock
                        old_sales = sku.sales

                        # 如果 购买个数 大于 库存stock
                        cart_count = carts_dict[sku_id]['count']
                        if cart_count > sku.stock:
                            # <3> 事务回滚
                            transaction.savepoint_rollback(save_id)
                            return http.JsonResponse({'code': RETCODE.STOCKERR, 'errmsg': '库存不足'})

                        # 延时--演示资源竞争
                        # (7号库存只有5个,但是显示两个人(3台 共6台)都成功了--赔钱)
                        # 但tb_sku中显示 5  0 -->2  3
                        # time.sleep(10)

                        # 4.SKU 销量增加 库存减少
                        # sku.stock -= cart_count
                        # sku.sales += cart_count
                        # sku.save()

                        # 新库存=老库存-购物车数量
                        new_stock = old_stock - cart_count
                        new_sales = old_sales + cart_count
                        # 使用乐观锁 执行更新(在每次操作数据库之前 先再次查询原始的库存是否改变,如果有改变就更新失败)
                        # 若更新失败--但库存仍然满足 则循环执行更新直到--库存不足或者购买成功 result返回 0或1
                        result = SKU.objects.filter(id=sku_id, stock=old_stock).update(stock=new_stock, sales=new_sales)

                        # 下单失败--直到 是因为库存不足或者购买成功的原因才退出循环
                        if result == 0:
                            continue

                        # 5.SPU 销量增加
                        sku.spu.sales += cart_count
                        sku.spu.save()

                        # 保存订单商品表的数据  <第4张表> OrderGoods
                        OrderGoods.objects.create(
                            order=order,
                            sku=sku,
                            count=cart_count,
                            price=sku.price,
                        )

                        # 重新计算 购买的总个数  总金额  运费
                        order.total_count += cart_count
                        order.total_amount += sku.price * cart_count

                        # 购买成功 退出循环购买
                        break

                # 总支付金额 需要加上运费
                order.total_amount += order.freight
                order.save()

            except Exception as e:
                # <5> 暴力回滚--三张表不管哪个有问题都回滚
                transaction.savepoint_rollback(save_id)
                return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '下单失败'})

            # <4> 事务提交
            transaction.savepoint_commit(save_id)

        # 6.清空购物车所有数据(已经购买的数据 以前选中的数据)
        redis_client.hdel(user.id, *carts_dict)

        # 7.返回响应对象
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '下单成功', 'order_id': order.order_id})