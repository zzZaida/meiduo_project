import json

from django import http
from django.shortcuts import render
from django.views import View

from apps.goods.models import SKU


class CartsView(View):
    """购物车管理"""

    def post(self, request):
        """添加购物车"""

        # 1.接收参数
        json_dict = json.loads(request.body.decode())
        sku_id = json_dict.get('sku_id')
        count = json_dict.get('count')
        selected = json_dict.get('selected', True)

        # 2.校验参数
        # 判断参数是否齐全
        if not all([sku_id, count]):
            return http.HttpResponseForbidden('缺少必传参数')
        # 2.1 商品是否存在
        try:
            SKU.objects.get(id=sku_id)
        except Exception as e:
            return http.HttpResponseForbidden('商品不存在')
        # 2.2 count 是不是 int
        try:
            count = int(count)
        except Exception as e:
            return http.HttpResponseForbidden('参数count不是整型')
        # 2.3 selected 是不是 boolean --> instance 实例化
        if selected:
            if not isinstance(selected, bool):
                return http.HttpResponseForbidden('参数selected不是布尔类型')

        # 3.判断是否登录  is_authenticated --> 装饰器 @property
        user = request.user
        if user.is_authenticated:
            # true--> 登录 redis
            print('登录 redis')
        else:
            # false-->未登录 cookie
            print('未登录 cookie')
