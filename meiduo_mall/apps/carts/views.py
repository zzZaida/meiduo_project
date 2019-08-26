import json

from django import http
from django.shortcuts import render
from django.views import View
from django_redis import get_redis_connection

from apps.goods.models import SKU
from utils.response_code import RETCODE
from utils.cookiesecret import CookieSecret


class CartsView(View):
    """购物车管理"""

    # 1.增加
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
            #  "user_id1":{"sku_id":{"count":"1","selected":"True"},

            # 1 链接数据库 redis
            redis_client = get_redis_connection('carts')

            # 2 取出所有的数据--> 从redis取出的数据--bytes
            # client_data = {b'3':b'{"count": 1,"selected": true}'}
            client_data = redis_client.hgetall(user.id)

            # 3 判断是否存在该用户是否有商品的记录数据
            if not client_data:  #   k       v     json.dumps(dict-->string)
                # 新增一条数据
                redis_client.hset(user.id, sku_id, json.dumps({'count': count, 'selected': selected}))

            # 4 判断当前添加的商品是否存在
            # client_data = {b'3':b'{"count": 1,"selected": true}'}
            if str(sku_id).encode() in client_data:
                # 修改count      dict(bytes-->string)
                sku_dict = json.loads(client_data[str(sku_id).encode()].decode())
                # 累加 前端传入的个数
                sku_dict["count"] += count
                redis_client.hset(user.id, sku_id, json.dumps(sku_dict))

            else:
                # 商品不存在 新建一条数据(给hash的数据对象新增属性)
                redis_client.hset(user.id, sku_id, json.dumps({'count': count, 'selected': selected}))

            # 5 返回响应对象
            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '添加购物车成功'})

        else:
            # false-->未登录 cookie
            # cookie_dict: {sku_id1: count, sku_id3: count, sku_id5: count, ...}

            # 1 查询cookie购物车数据
            cookie_str = request.COOKIES.get('carts')

            # 2 判断有没有
            from utils.cookiesecret import CookieSecret
            if cookie_str:
                # 3 有--解密
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
            response.set_cookie('carts', dumps_cookie_str, max_age=15 * 24 * 3600)

            # 7 返回响应对象
            return response

    # 2.查询--展示购物车
    def get(self, request):

        # 1.判断是否登录
        user = request.user
        if user.is_authenticated:
            # 用户已登录, 查询redis购物车
            # 1.链接数据库
            redis_client = get_redis_connection('carts')

            # 2.取出该用户所有购物车数据
            redis_carts_dict = redis_client.hgetall(user.id)

            # 3.字典推导式
            # carts_dict = {}
            # for key, value in redis_carts_dict.items():
            #     sku_id = int(key.decode())
            #     sku_value = json.loads(value.decode())
            #     carts_dict[sku_id] = sku_value

            carts_dict = {int(key.decode()): json.loads(value.decode()) for key, value in redis_carts_dict.items()}

        else:
            # 用户未登录, 查询cookies购物车
            cookie_str = request.COOKIES.get('carts')
            if cookie_str:
                carts_dict = CookieSecret.loads(cookie_str)
            else:
                carts_dict = {}

        # 前端需要的列表字典 -- cookie redis传给前端的数据格式保持一致 -->
        # cookie            {"sku_id":{"count":2, "selected":true}}
        # redis  {"user_id":{"sku_id":{"count":2, "selected":true }}}

        # carts_dict = {"sku_id": {"count": 2, "selected": True}}
        sku_ids = carts_dict.keys()  # sku_id

        # 根据范围查询sku_id 获取所有的 sku(商品) 对象
        skus = SKU.objects.filter(id__in=sku_ids)
        cart_skus = []
        for sku in skus:
            cart_skus.append({
                'id': sku.id,
                'name': sku.name,
                # dict.get(k, default=None)函数返回指定键的值  如果值不在字典中,返回默认值
                'count': carts_dict.get(sku.id).get('count'),
                'selected': str(carts_dict.get(sku.id).get('selected')),  # 将True，转'True'，方便json解析
                'default_image_url': sku.default_image.url,
                'price': str(sku.price),  # 从Decimal('10.2')中取出'10.2'，方便json解析
                'amount': str(sku.price * carts_dict.get(sku.id).get('count')),  # 总价
            })

        context = {
            'cart_skus': cart_skus,
        }

        return render(request, 'cart.html', context)
