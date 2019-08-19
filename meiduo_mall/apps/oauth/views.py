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