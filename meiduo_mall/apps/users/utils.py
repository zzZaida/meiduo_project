
# 1. 导包 认证后端的包
from django.contrib.auth.backends import ModelBackend
import re
from .models import User


def get_user_by_account(account):

    try:
        # 4.校验username 又校验手机号
        if re.match('^1[345789]\d{9}$', account):
            # 手机号
            user = User.objects.get(mobile=account)
        else:
            # username
            user = User.objects.get(username=account)

    except User.DoesNotExist:
        return None
    else:
        return user


# 2. 类继承
class UsernameMobileAuthBackend(ModelBackend):
    # 3.重写父类的 authenticate函数
    def authenticate(self, request, username=None, password=None, **kwargs):

        user = get_user_by_account(username)
        # 验证密码的正确性
        if user and user.check_password(password):
            return user

# 5. dev.py 改后端认证的配置
# 指定自定义的用户认证后端
# AUTHENTICATION_BACKENDS = ['apps.users.utils.UsernameMobileAuthBackend']
