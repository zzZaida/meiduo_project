from django.shortcuts import render
from django.views import View
import re

# 点完注册  DeBUG 有反应 到后台页面 ---> 前端问题
# from django.http import HttpResponseForbidden
from django import http



class RegisterView(View):
    # 1.注册页面显示
    def get(self,request):

        return render(request, 'register.html')

    # 2.注册功能
    def post(self,request):
        # 1 接收解析参数
        username = request.POST.get('username')
        # username = request.POST('username')  ‘QueryDict’ object is not callable(调用)
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        mobile = request.POST.get('mobile')
        allow = request.POST.get('allow')

        # 2 校验参数
        # * 0.判空
        if not all([username, password, password2, mobile, allow]):
            return http.HttpResponseForbidden('缺少参数！')
        # * 1.用户名: ---------判空,正则校验,是否重复
        if not re.match('^[a-zA-Z0-9_-]{5,20}$', username):
            return http.HttpResponseForbidden('请输入5-20个字符的用户名')
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

        # * 7.同意”美多商城用户使用协议“: 判断是否选中
        if allow != 'on':
            return http.HttpResponseForbidden('请求协议！')
        print('后台请求')
        # 3 注册用户

        # 4 重定向到首页
