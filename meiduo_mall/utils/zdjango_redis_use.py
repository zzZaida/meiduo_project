

def demo():
    # 1 导包
    from django_redis import get_redis_connection

    # 2 链接数据库
    client = get_redis_connection('default')
    # client = get_redis_connection('session') --> 进一号数据库

    # 3 增删改查
    # 存进去
    client.set('django_redis_key', 'meiduo')
    # 取出来
    result = client.get('django_redis_key')
    # 千万注意：取出的 redis 的数据类型是 bytes
    print(result)

# 报错  --> 单独运行这个文件  代码没问题
# Requested setting CACHES, but settings are not configured.
# You must either define the environment variable DJANGO_SETTINGS_MODULE or call settings.configure() before accessing settings.


# >>> from utils import zdjango_redis_use
# >>> zdjango_redis_use.demo()
# 报错 ：Connection refused
# 开启 redis 服务  --> redis-server
# b'meiduo'    ----> bytes
