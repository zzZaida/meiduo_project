# 1.合并方向：cookie购物车数据合并到Redis购物车数据中。
# 2.合并数据：购物车商品数据和勾选状态。
# 3.合并方案：
#     3.1 Redis数据库中的购物车数据保留。
#     3.2 如果cookie中的购物车数据在Redis数据库中已存在，将cookie购物车数据覆盖Redis购物车数据。
#     3.3 如果cookie中的购物车数据在Redis数据库中不存在，将cookie购物车数据新增到Redis。
import json
from django_redis import get_redis_connection
from utils.cookiesecret import CookieSecret


def merge_cart_cookie_to_redis(request, user, response):

    # 1.cookie_dict
    cookie_str = request.COOKIES.get('carts')
    if cookie_str:
        cookie_dict = CookieSecret.loads(cookie_str)
    else:
        cookie_dict = {}
        return response

    # 2.redis_dict
    redis_client = get_redis_connection('carts')
    client_data_dict = redis_client.hgetall(user.id)

    # carts_dict = {}
    # for data in client_data_dict.items():
    #     sku_id = int(data[0].decode())
    #     sku_dict = json.loads(data[1].decode())
    #     carts_dict[sku_id] = sku_dict

    redis_dict = {int(data[0].decode()): json.loads(data[1].decode()) for data in client_data_dict.items()}

    # 3.合并  redis_dict.update(cookie_dict)
    redis_dict.update(cookie_dict)

    # 4.重新插入数据库redis
    # carts_dict = {"sku_id":{"count":count, "selected":selected}}
    for sku_id in redis_dict:
        #       hset(self, name,   key,      value)
        redis_client.hset(user.id, sku_id, json.dumps(redis_dict[sku_id]))

    # 5.删除cookie
    response.delete_cookie('carts')

    return response