import json
from asyncio import constants

from django.conf import settings
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

from apps.areas.models import Address
from apps.users.models import User
from apps.verifications import contants
from meiduo_mall.settings.development import logger
from utils.response_code import RETCODE


# 1 注册页面
class RegisterView(View):
    # 1.注册页面显示
    def get(self, request):

        return render(request, 'register.html')

    # 2.注册功能
    def post(self, request):
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
        # * 1.用户名: ---------判空,正则校验,是否重复
        if not re.match('^[a-zA-Z0-9_-]{5,20}$', username):
            return http.HttpResponseForbidden('请输入5-20个字符的用户名')
        # 判断用户名是否重复 ---- username-->给后台传递-->接收参数-->后台2次校验参数-->查询filter().count()

        # * 2.密码:   --------- 判空,正则校验
        if not re.match('^[0-9A-Za-z]{8,20}$', password):
            return http.HttpResponseForbidden('请输入8-20位的密码')
        # * 3.确认密码: ---------判空,判断是否相等
        if password2 != password:
            return http.HttpResponseForbidden('两次密码输入不一致')
        # * 4.手机号:---------   判空,正则校验,是否重复
        if not re.match('^1[345789]\d{9}$', mobile):
            return http.HttpResponseForbidden('请输入正确的手机号码')

        # * 5.图形验证码
        # * 6.短信验证码
        sms_code = request.POST.get('msg_code')

        from django_redis import get_redis_connection
        sms_client = get_redis_connection('sms_code')
        sms_code_redis = sms_client.get('sms_%s' % mobile)

        if sms_code_redis is None:
            return render(request, 'register.html', {'sms_code_errmsg': '无效的短信验证码'})
        # 删除 sms_code_redis
        sms_client.delete('sms_%s' % mobile)

        if sms_code != sms_code_redis.decode():
            return render(request, 'register.html', {'sms_code_errmsg': '短信验证码有误!'})

        # * 7.同意”美多商城用户使用协议“: 判断是否选中
        if allow != 'on':
            return http.HttpResponseForbidden('请求协议！')
        #
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
    def get(self, request):
        return render(request, 'login.html')

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

        # 3.验证用户名和密码(数据交互)--django自带的认证 authenticate()
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
        # 6.1 登录优化--> 未登录--点击个人中心-->登录页面-->个人中心
        # http://www.meiduo.site:8000/login/?next=/info/
        next = request.GET.get('next')
        if next:
            response = redirect(next)
        else:
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
        # request.user.username
        context = {
            'username': request.user.username,
            'mobile': request.user.mobile,
            'email': request.user.email,
            'email_active': request.user.email_active
        }
        return render(request, 'user_center_info.html', context)


# 7 邮箱添加
class EmailView(LoginRequiredMixin, View):
    def put(self, request):
        # 1.接收 请求体非表单参数 json
        json_bytes = request.body
        json_str = json_bytes.decode()
        json_dict = json.loads(json_str)
        email = json_dict.get('email')

        # 2.正则校验邮箱
        if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return http.HttpResponseForbidden('参数email有误')

        # 3.修改 数据库中 email 值
        try:
            request.user.email = email
            request.user.save()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '添加邮箱失败'})

        # 自动发邮件(需要加密)
        token_value = {
            'user_id': request.user.id,
            'email': email
        }
        # 加密 --->对象方法SecretOauth()
        from utils.secret import SecretOauth
        secret_str = SecretOauth().dumps(token_value)
        # http://www.meiduo.site:8000/emails/verification/?token={%22user_id%22:%201,%20%22email%22:%20%2217638121602@163.com%22}
        verify_url = settings.EMAIL_ACTIVE_URL + "?token=" + secret_str
        from celery_tasks.email.tasks import send_verify_email
        send_verify_email.delay(email, verify_url)

        # 4.返回前端结果
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '添加邮箱成功'})


# 8 激活邮箱  /emails/verification/
# http://www.meiduo.site:8000/emails/verification/
# ?token={
# "user_id": 1, "email": "17638121602@163.com"}

def check_verify_email_token(token):
    # 解密
    from utils.secret import SecretOauth
    json_dict = SecretOauth().loads(token)
    # 校验用户是否存在  同时邮箱也匹配
    try:
        user = User.objects.get(id=json_dict['user_id'], email=json_dict['email'])
    except Exception as e:
        logger.error(e)
        return None
    else:
        return user


class VerifyEmailView(LoginRequiredMixin, View):
    def get(self, request):
        # 1.接收参数
        json_str = request.GET.get('token')

        # 校验用户是否存在  同时邮箱也匹配
        user = check_verify_email_token(json_str)
        if not user:
            return http.HttpResponseForbidden('无效的token')

        # 2.修改对象的 email_active 字段
        try:
            user.email_active = True
            user.save()
        except Exception as e:
            logger.error(e)
            return http.HttpResponseForbidden('激活邮箱失效了!')

        # 3.返回响应结果
        return redirect(reverse('users:info'))


# 9 查询收货地址
class AddressView(LoginRequiredMixin, View):
    def get(self, request):
        # 1.查询当前用户的 所有地址
        user = request.user
        addresses = Address.objects.filter(user=user, is_deleted=False)

        # 2.构建前端需要的数据格式
        address_dict_list = []
        for address in addresses:
            address_dict = {
                "id": address.id,
                "title": address.title,
                "receiver": address.receiver,
                "province": address.province.name,
                "city": address.city.name,
                "district": address.district.name,
                "place": address.place,
                "mobile": address.mobile,
                "tel": address.tel,
                "email": address.email
            }
            address_dict_list.append(address_dict)

        context = {
            'default_address_id': user.default_address_id,
            'addresses': address_dict_list,
        }
        return render(request, 'user_center_site.html', context)


# 10 增加收货地址
class CreateAddressView(LoginRequiredMixin, View):
    def post(self, request):

        # 判断是否超过地址上限：最多20个
        count = Address.objects.filter(user=request.user, is_deleted=False).count()
        # count = request.user.addresses.filter(is_deleted=False).count()
        if count >= constants.USER_ADDRESS_COUNTS_LIMIT:
            return http.JsonResponse({'code': RETCODE.THROTTLINGERR, 'errmsg': '超过地址数量上限'})

        # 1.接收参数 JSON   dict(bytes-->string)
        json_dict = json.loads(request.body.decode())

        receiver = json_dict.get('receiver')
        province_id = json_dict.get('province_id')
        city_id = json_dict.get('city_id')
        district_id = json_dict.get('district_id')
        place = json_dict.get('place')
        mobile = json_dict.get('mobile')
        tel = json_dict.get('tel')
        email = json_dict.get('email')

        # 2.正则校验
        if not all([receiver, province_id, city_id, district_id, place, mobile]):
            return http.HttpResponseForbidden('缺少必传参数')
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.HttpResponseForbidden('参数mobile有误')
        if tel:
            if not re.match(r'^(0[0-9]{2,3}-)?([2-9][0-9]{6,7})+(-[0-9]{1,4})?$', tel):
                return http.HttpResponseForbidden('参数tel有误')
        if email:
            if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
                return http.HttpResponseForbidden('参数email有误')

        # 3.create
        # 保存地址信息
        try:
            address = Address.objects.create(
                user=request.user,
                title=receiver,
                receiver=receiver,
                province_id=province_id,
                city_id=city_id,
                district_id=district_id,
                place=place,
                mobile=mobile,
                tel=tel,
                email=email
            )

            # 设置默认地址
            default_address = request.user.default_address
            if not default_address:
                request.user.default_address = address
                request.user.save()

        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '新增地址失败'})

        # 4.构建前端  dict
        address_dict = {
            "id": address.id,
            "title": address.title,
            "receiver": address.receiver,
            "province": address.province.name,
            "city": address.city.name,
            "district": address.district.name,
            "place": address.place,
            "mobile": address.mobile,
            "tel": address.tel,
            "email": address.email
        }

        # 5.返回  JsonResponse:  dict-->JSONstring
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '新增地址成功', 'address': address_dict})
