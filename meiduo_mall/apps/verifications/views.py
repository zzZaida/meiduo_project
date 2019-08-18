from django import http
from django.shortcuts import render
from django.views import View
from apps.verifications import contants
from meiduo_mall.settings.development import logger


# <4> 图片验证码 image_codes/(?P<uuid>[\w-]+)/
class ImageCodeView(View):
    # UUID 唯一标识符
    def get(self, request, uuid):

        # 1 接收参数
        # 2 校验 uuid 正则

        # 3 生成图片验证码
        from libs.captcha.captcha import captcha
        text, image = captcha.generate_captcha()

        # 4 验证码数字  存储到 redis
        # 4.1 导包
        from django_redis import get_redis_connection
        # 4.2 链接数据库
        img_client = get_redis_connection('image_code')
        # 4.3 存储  setex设置过期时间  5min--300s
        img_client.setex(uuid, contants.IMAGE_CODE_REDIS_EXPIRE, text)

       # 5 给前端返回 图片验证码 bytes
        return http.HttpResponse(image, content_type='image/jpeg')


# <5> 短信验证码 /sms_codes/(?P<mobile>1[3-9]\d{9})/
class SMSCodeView(View):
    def get(self, request, mobile):
        # 1. 接收 2个 mobile; 图片验证码img_code
        image_code = request.GET.get('image_code')
        uuid = request.GET.get('image_code_id')

        # 2.验证码 img_code和redis存储的验证码 是否一致 (1 redis取出来(4步) 2 判断是否相等)
        from django_redis import get_redis_connection
        img_client = get_redis_connection('verify_image_code')
        img_code_redis = img_client.get('img_%s' % uuid)

        # 2.1 判断是否为空
        if img_code_redis is None:
            return http.JsonResponse({'code': "4001", 'errmsg': '图形验证码失效了'})
        # 2.2 删除图片验证码
        img_client.delete('img_%s' % uuid)
        # 2.3 判断是否相等  千万注意: redis返回的是bytes类型
        if img_code_redis.decode().lower() != image_code.lower():
            return http.JsonResponse({'code': "4001", 'errmsg': '输入图形验证码有误'})

        print('成功没有!')

        # 3.生成随机6位 短信验证码内容 random.randit()
        # 4.存储 随机6位 redis(3步)
        # 5.发送短信-- 第三方联容云--
        # 6.返回响应对象






















        # # 1.解析校验参数--mobile 不用校验
        # uuid = request.GET.get('image_code_id')
        # image_code = request.GET.get('image_code')
        #
        # # 2.校验图形验证码 如果正确 发送验证码, 不正确 直接返回
        # # 2.1 根据uuid 去redis数据库查询 图片验证码
        # from django_redis import get_redis_connection
        # image_redis_client = get_redis_connection('verify_image_code')
        # redis_img_code = image_redis_client.get('img_%s' % uuid)
        #
        # # 判断服务器返回的验证
        # if redis_img_code is None:
        #     return http.JsonResponse({'code': "4001", 'errmsg': '图形验证码失效了'})
        #
        # # 如果有值 删除redis服务器上的图形验证码
        # try:
        #     image_redis_client.delete('img_%s' % uuid)
        # except Exception as e:
        #     logger.error(e)
        #
        # # 2.2 和前端传过来的进行做对比
        # # 千万注意: 在redis取出来的是 bytes 类型不能直接做对比 decode()
        # if image_code.lower() != redis_img_code.decode().lower():
        #     return http.JsonResponse({'code': "4001", 'errmsg': '输入图形验证码有误'})
        #
        # # 3.生成短信验证码,redis-存储
        # from random import randint
        # sms_code = "%06d" % randint(100000, 999999)
        # sms_redis_client = get_redis_connection('sms_code')
        # sms_redis_client.setex("sms_%s" % mobile, contants.SMS_CODE_REDIS_EXPIRE, sms_code)
        #
        # # 4.让第三方 容联云-给手机号-发送短信
        # from libs.yuntongxun.sms import CCP
        # #               ,类型默认1
        # #  CCP().send_template_sms('手机号', ['验证码', '过期时间5分钟'], 短信模板1)
        # # CCP().send_template_sms(mobile, [sms_code, 5], 1)
        # print("当前验证码是:", sms_code)
        #
        # # 5.告诉前端短信发送完毕
        # return http.JsonResponse({'code': '0', 'errmsg': '发送短信成功'})