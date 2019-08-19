from django import http
from django.shortcuts import render
from django.views import View

# QQ_CLIENT_ID = '101518219'
# QQ_CLIENT_SECRET = '418d84ebdc7241efb79536886ae95224'
# QQ_REDIRECT_URI = 'http://www.meiduo.site:8000/oauth_callback'
# uri > url

from QQLoginTool.QQtool import OAuthQQ
from django.conf import settings
from utils.response_code import RETCODE


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

        return http.HttpResponse(openid)
    # EA3AB309F7F6384FE165C3234B061ECC
