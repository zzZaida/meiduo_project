import json

from django import http
from django.shortcuts import render
from django.views import View

from apps.goods.models import SKU
from utils.response_code import RETCODE


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

            # 1 查询cookie购物车数据
            cookie_str = request.COOKIES.get('carts')

            # 2 判断有没有cookie
            from utils.cookiesecret import CookieSecret
            if cookie_str:
                # 3 有--解密 cookie
                cookie_dict = CookieSecret.loads(cookie_str)
            else:
                # 没有--新建一个
                cookie_dict = {}

            # ***判断商品是否 存在购物车里面
            if sku_id in cookie_dict:
                original_count = cookie_dict[sku_id]['count']
                count += original_count

            # 4 修改 count selected
            cookie_dict[sku_id] = {
                'count': count,
                'selected': selected
            }

            # 5 加密 cookie
            dumps_cookie_str = CookieSecret.dumps(cookie_dict)

            # 6 设置增加cookie--> set_cookie()
            response = http.JsonResponse({'code': RETCODE.OK, 'errmsg': '添加购物车成功'})
            response.set_cookie('carts', dumps_cookie_str, max_age=15*24*3600)

            # 7 返回响应对象
            return response

