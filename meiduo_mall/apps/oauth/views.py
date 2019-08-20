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

from apps.oauth.models import OAuthQQUser
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
