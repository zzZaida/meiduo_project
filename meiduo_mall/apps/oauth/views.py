import re

from django import http
from django.contrib.auth import login
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View

# QQ_CLIENT_ID = '101518219'
# QQ_CLIENT_SECRET = '418d84ebdc7241efb79536886ae95224'
# QQ_REDIRECT_URI = 'http://www.meiduo.site:8000/oauth_callback'
# uri > url

from QQLoginTool.QQtool import OAuthQQ
from django.conf import settings
from django_redis import get_redis_connection

from apps.carts.utils import merge_cart_cookie_to_redis
from apps.oauth.models import OAuthQQUser
from apps.users.models import User
from utils.response_code import RETCODE


# 4. 使用openid查询该QQ用户是否在美多商城中绑定过用户
def is_bind_openid(openid, request):

    try:
        # 1 如果数据表中存在openid --- 绑定了
        oauth_user = OAuthQQUser.objects.get(openid=openid)
    except Exception as e:
        # 2 数据表中不存在openid --- 没有绑定
        print(openid)
        return render(request, 'oauth_callback.html', context={'openid':openid})
    else:
        user = oauth_user.user
        # 3 保持登录状态
        login(request, user)
        # 4 重定向到首页 设置首页用户名
        response = redirect(reverse('contents:index'))
        response.set_cookie('username', user.username, max_age=24*14*3600)
        return response


# 1 客户端与美多商城交互
class QQAuthURLView(View):
    def get(self, request):

        # 1.返回QQ登录地址--和QQ平台认证通过 实例化认证对象
        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID,
                        client_secret=settings.QQ_CLIENT_SECRET,
                        redirect_uri=settings.QQ_REDIRECT_URI)

        # 2.获取qq_login_url
        login_url = oauth.get_qq_url()

        # 3.返回给前端
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'login_url': login_url})


# http://www.meiduo.site:8000
# /oauth_callback?code=8FFD3C39375F28B6D0E9CE5FC14EF25C&state=None

# 2 与QQ交互--> 接收 QQ 返回来的 code--> 获取openid
class QQAuthUserView(View):
    # 显示
    def get(self, request):
        # 1.解析参数
        code = request.GET.get('code')
        # 认证
        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID,
                        client_secret=settings.QQ_CLIENT_SECRET,
                        redirect_uri=settings.QQ_REDIRECT_URI)

        # 2. code-->token
        token = oauth.get_access_token(code)

        # 3. token-->openid
        openid = oauth.get_open_id(token)

        # 4. 是否绑定openid
        response = is_bind_openid(openid, request)
        return response

        # return http.HttpResponse(openid)
        # EA3AB309F7F6384FE165C3234B061ECC

    # 增加  保存
    def post(self, request):
        """美多商城用户绑定到openid"""

        # 1.接收参数
        mobile = request.POST.get('mobile')
        pwd = request.POST.get('password')
        sms_code_client = request.POST.get('sms_code')
        openid = request.POST.get('openid')

        # 2.判空正则校验 图片验证 短信验证
        # 判断参数是否齐全
        if not all([mobile, pwd, sms_code_client]):
            return http.HttpResponseForbidden('缺少必传参数')
        # 判断手机号是否合法
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.HttpResponseForbidden('请输入正确的手机号码')
        # 判断密码是否合格
        if not re.match(r'^[0-9A-Za-z]{8,20}$', pwd):
            return http.HttpResponseForbidden('请输入8-20位的密码')
        # # 判断短信验证码是否一致
        # redis_conn = get_redis_connection('sms_code')
        # sms_code_server = redis_conn.get('sms_%s' % mobile)
        # if sms_code_server is None:
        #     return render(request, 'oauth_callback.html', {'sms_code_errmsg': '无效的短信验证码'})
        # if sms_code_client != sms_code_server.decode():
        #     return render(request, 'oauth_callback.html', {'sms_code_errmsg': '输入短信验证码有误'})
        # # 解密出openid 再判断openid是否有效
        # openid = SecretOauth().loads(openid).get('openid')
        # if not openid:
        #     return render(request, 'oauth_callback.html', {'openid_errmsg': '无效的openid'})

        # 3.判断user是否存在
        try:
            user = User.objects.get(mobile=mobile)
        except Exception as e:
            # 没注册--> 新注册一个
            user = User.objects.create_user(username=mobile, mobile=mobile, password=pwd)
        else:
            # 注册了--> 校验密码
            if not user.check_password(pwd):
                return render(request, 'oauth_callback.html', {'account_errmsg': '用户名或密码错误'})

        # 4.绑定openid
        try:
            OAuthQQUser.objects.create(user=user, openid=openid)
        except Exception as e:
            return render(request, 'oauth_callback.html', {'qq_login_errmsg': 'QQ登录失败'})

        # 5.重定向到首页
        # 保持登录状态
        login(request, user)
        # 重定向到首页 设置首页用户名
        response = redirect(reverse('contents:index'))

        # 购物车合并
        # cookie--未登录--笔记本1  黄色2  黑色3  银色1
        # redis----登录---笔记本3  黄色2  黑色1
        # 合并结果---           1     2     3     1
        response = merge_cart_cookie_to_redis(request, user, response)

        response.set_cookie('username', user.username, max_age=24 * 14 * 3600)
        return response

