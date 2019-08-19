from django import http
from django.shortcuts import render
from django.views import View
from apps.verifications import contants
from meiduo_mall.settings.development import logger
from utils.response_code import RETCODE


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
        img_client = get_redis_connection('verify_image_code')
        # 4.3 存储  setex设置过期时间  5min--300s
        img_client.setex('img_%s' % uuid, contants.IMAGE_CODE_REDIS_EXPIRE, text)

       # 5 给前端返回 图片验证码 bytes
        return http.HttpResponse(image, content_type='image/jpeg')


# <5> 短信验证码 /sms_codes/(?P<mobile>1[3-9]\d{9})/
class SMSCodeView(View):
    def get(self, request, mobile):
        # 1. 接收 2个 mobile; 图片验证码img_code
        uuid = request.GET.get('image_code_id')
        image_code = request.GET.get('image_code')

        # 2.验证码 img_code和redis存储的验证码 是否一致 (1.redis取出来(4步) 2.判断是否相等 3.redis img_code 删除)
        from django_redis import get_redis_connection
        img_client = get_redis_connection('verify_image_code')
        img_code_redis = img_client.get('img_%s' % uuid)
        # 2.1 判断是否为空
        if img_code_redis is None:
            return http.JsonResponse({'code': "4001", 'errmsg': '图形验证码失效了'})
        # 2.2 删除图片验证码
        try:
            img_client.delete('img_%s' % uuid)
        except Exception as e:
            logger.error(e)
        # 2.3 判断是否相等  千万注意: redis返回的是bytes类型
        if img_code_redis.decode().lower() != image_code.lower():
            return http.JsonResponse({'code': "4001", 'errmsg': '输入图形验证码有误'})
        print('成功没有!')

        # 3.生成随机6位 短信验证码内容 random.randit()
        from random import randint
        sms_code = "%06d" % randint(0, 999999)

        # 4.存储 随机6位 redis(3步)
        sms_client = get_redis_connection('sms_code')
        print(sms_code)
        # 后台避免 短信验证码重复流程
        # (1)获取 频繁发送短信的 标识
        send_flag = sms_client.get('send_flag_%s' % mobile)
        # (2)判断标识是否存在
        if send_flag:
            # return http.JsonResponse({'code': RETCODE.THROTTLINGERR, 'errmsg': '发送短信过于频繁'})
            return http.JsonResponse({'code': "4002", 'errmsg': '发送短信过于频繁666'})
        # (3)标识不存在,  重新倒计时
        # 保存短信验证码
        # sms_client.setex('sms_%s' % mobile, contants.SMS_CODE_REDIS_EXPIRE, sms_code)
        # 重新写入send_flag
        # sms_client.setex('send_flag_%s' % mobile, contants.SEND_SMS_CODE_INTERVAL, 1)

        # pipeline操作Redis数据库---> 通过减少客户端与Redis的通信次数来实现降低往返延时时间
        # 创建Redis管道
        pl = sms_client.pipeline()
        # 将Redis请求添加到队列
        pl.setex('sms_%s' % mobile, contants.SMS_CODE_REDIS_EXPIRE, sms_code)
        pl.setex('send_flag_%s' % mobile, contants.SEND_SMS_CODE_INTERVAL, 1)
        # 执行请求
        pl.execute()

        # 5.发送短信-- 第三方联容云--
        # from libs.yuntongxun.sms import CCP
        #  CCP().send_template_sms('手机号', ['验证码', '过期时间5分钟'], 短信模板1)
        # CCP().send_template_sms(mobile, [sms_code, 5], 1)
        # print("当前验证码是:", sms_code)

        # 使用异步发---触发任务
        from celery_tasks.sms.tasks import ccp_send_sms_code
        ccp_send_sms_code.delay(mobile, sms_code)

        # 6.返回响应对象
        return http.JsonResponse({'code': '0', 'errmsg': '发送短信成功'})

