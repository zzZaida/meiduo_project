

# 绑定QQ的标识 和 美多的用户
# 定义QQ身份（openid）与用户模型类User的关联关系
from django.db import models
# 自定义的时间基类--> 用于继承
from utils.models import BaseModel


class OAuthQQUser(BaseModel):
    """QQ登录用户数据"""
    # db_index=True 查询索引
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, verbose_name='用户')
    openid = models.CharField(max_length=64, verbose_name='openid', db_index=True)

    class Meta:
        db_table = 'tb_oauth_qq'
        verbose_name = 'QQ登录用户数据'
        verbose_name_plural = verbose_name

# 迁移QQ登录模型类
# $ python manage.py makemigrations
# $ python manage.py migrate
