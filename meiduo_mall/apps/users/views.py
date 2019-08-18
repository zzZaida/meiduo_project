from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
import re

# 点完注册  DeBUG 有反应 到后台页面 ---> 前端问题
# from django.http import HttpResponseForbidden
from django import http

from apps.users.models import User
from apps.verifications import contants
from meiduo_mall.settings.development import logger
from utils.response_code import RETCODE


# 1 注册页面
class RegisterView(View):
    # 1.注册页面显示
    def get(self,request):

        return render(request, 'register.html')

    # 2.注册功能
    def post(self,request):
        # <1> 接收解析参数
        username = request.POST.get('username')
        # username = request.POST('username')  ‘QueryDict’ object is not callable(调用)
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        mobile = request.POST.get('mobile')
        allow = request.POST.get('allow')

        # <2> 校验参数
        # * 0.判空
        # if not all([username, password, password2, mobile, allow]):
        #     return http.HttpResponseForbidden('缺少参数！')
        # # * 1.用户名: ---------判空,正则校验,是否重复
        # if not re.match('^[a-zA-Z0-9_-]{5,20}$', username):
        #     return http.HttpResponseForbidden('请输入5-20个字符的用户名')
        # # 判断用户名是否重复 ---- username-->给后台传递-->接收参数-->后台2次校验参数-->查询filter().count()
        #
        # # * 2.密码:   --------- 判空,正则校验
        # if not re.match('^[0-9A-Za-z]{8,20}$', password):
        #     return http.HttpResponseForbidden('请输入8-20位的密码')
        # # * 3.确认密码: ---------判空,判断是否相等
        # if password2 != password:
        #     return http.HttpResponseForbidden('两次密码输入不一致')
        # # * 4.手机号:---------   判空,正则校验,是否重复
        # if not re.match('^1[345789]\d{9}$', mobile):
        #     return http.HttpResponseForbidden('请输入正确的手机号码')
        #
        # # * 5.图形验证码
        # # * 6.短信验证码
        # sms_code = request.POST.get('msg_code')
        #
        # from django_redis import get_redis_connection
        # sms_client = get_redis_connection('sms_code')
        # sms_code_redis = sms_client.get('sms_%s' % mobile)
        #
        # if sms_code_redis is None:
        #     return render(request, 'register.html', {'sms_code_errmsg': '无效的短信验证码'})
        # # 删除 sms_code_redis
        # sms_client.delete('sms_%s' % mobile)
        #
        # if sms_code != sms_code_redis.decode():
        #     return render(request, 'register.html', {'sms_code_errmsg': '短信验证码有误!'})
        #
        # # * 7.同意”美多商城用户使用协议“: 判断是否选中
        # if allow != 'on':
        #     return http.HttpResponseForbidden('请求协议！')

        # <3> 注册用户
        # Duplicate(重复) entry 'itcast1' for key 'username'
        # 交互数据库的地方 最好预处理
        try:
            # from apps.users.models import User  --> 自定义用户类User
            user = User.objects.create_user(username=username, password=password, mobile=mobile)
        except Exception as e:
            logger.error(e)
            return render(request, 'register.html')

        # <4> 保持登录状态：cookie --session(django自带)
        # from django.contrib.auth import login
        login(request, user)

# redis-cli
# 127.0.0.1:6379> keys *
# 1) "django_redis_key"
# 127.0.0.1:6379> select 1
# OK
# 127.0.0.1:6379[1]> keys *
# 1) ":1:django.contrib.sessions.cachekd572q3dxu4g6oxagre9bcor1w5o8wxb"
# 127.0.0.1:6379[1]> get :1:django.contrib.sessions.cachekd572q3dxu4g6oxagre9bcor1w5o8wxb
# "\x80\x04\x95\x97\x00\x00\x00\x00\x00\x00\x00}\x94(\x8c\x0f_auth_user_hash\x94\x8c(63f00bc33873fb5c9317bc8366da5d8676531df8
# \x94\x8c\r_auth_user_id\x94\x8c\x018\x94\x8c\x12_auth_user_backend\x94\x8c)django.contrib.auth.backends.ModelBackend\x94u."

    # <5> 重定向到首页
        # return http.HttpResponse('重定向到首页')
        # 响应注册结果
        response = redirect(reverse('contents:index'))
        # 注册时用户名写入到cookie，有效期15天
        response.set_cookie('username', user.username, max_age=3600 * 24 * 15)
        return response


# 2 判断用户名是否重复
class UsernameCountView(View):
    def get(self, request, username):
        # 1 接收参数
        # 2 校验正则
        if not re.match('^[a-zA-Z0-9_-]{5,20}$', username):
            return http.HttpResponseForbidden('请输入5-20个字符的用户名')
        # 3 查询数据库的用户名
        count = User.objects.filter(username=username).count()
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'count': count})


# 3 判断手机号是否重复
# 后端接口认证 --->   http://www.meiduo.site:8000/mobiles/17638121602/count/
class MobileCountView(View):
    def get(self, request, mobile):
        # 1 接收参数
        # 2 校验正则
        if not re.match('^1[345789]\d{9}$', mobile):
            return http.HttpResponseForbidden('请输入正确的手机号码')
        # 3 查询数据库 mobile 字段   返回个数
        count = User.objects.filter(mobile=mobile).count()
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'count': count})


# 4 登录
class LoginView(View):
    def get(self,request):
        return render(request,'login.html')

    def post(self, request):
        # 1.接收三个参数
        username = request.POST.get('username')
        password = request.POST.get('password')
        remembered = request.POST.get('remembered')

        # 2.校验参数
        if not all([username, password]):
            return HttpResponseForbidden('参数不齐全')
        # 2.1 用户名
        if not re.match(r'^[a-zA-Z0-9_-]{5,20}$', username):
            return HttpResponseForbidden('请输入5-20个字符的用户名')
        # 2.2 密码
        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return HttpResponseForbidden('请输入8-20位的密码')

        # 3.验证用户名和密码(数据交互)--django自带的认证
        from django.contrib.auth import authenticate, login
        user = authenticate(username=username, password=password)

        if user is None:
            return render(request, 'login.html', {'account_errmsg': '用户名或密码错误'})

        # 4.保持登录状态: cookie ---session
        # from django.contrib.auth import login
        login(request, user)

        # 5.是否记住用户名
        if remembered != 'on':
            # 不记住用户名, 浏览器结束会话就过期
            request.session.set_expiry(0)
        else:
            # 记住用户名, 浏览器会话保持两周
            request.session.set_expiry(None)

        # 6.返回响应结果  跳转到首页  index
        response = redirect(reverse('contents:index'))
        # 注册时用户名写入到cookie,有效期15天
        response.set_cookie('username', user.username, max_age=contants.SET_COOKIE_EXPIRE)
        return response


# 5 退出登录
class LogoutView(View):
    def get(self, request):
        # 1.退出的本质 (删除session)
        from django.contrib.auth import logout
        logout(request)

        # 重定向到登录页面
        # 2.清空cookie --首页用户名
        response = redirect(reverse('users:login'))
        response.delete_cookie('username')

        return response

# 6 个人中心 ---隐私信息LoginRequiredMixin
# from django.contrib.auth.mixins import LoginRequiredMixin
class UserInfoView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request,'user_center_info.html')
