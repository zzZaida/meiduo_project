from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.


class User(AbstractUser):
    """自定义用户模型类"""
    # 系统自带 username password(加解密)
    """新增 mobile 手机号 字段"""
    mobile = models.CharField(max_length=11, unique=True, verbose_name='手机号')

    """新增 邮箱是否激活的 字段"""
    email_active = models.BooleanField(default=False, verbose_name='邮箱验证状态')

    """新增 默认地址 字段"""
    default_address = models.ForeignKey('areas.Address', related_name='users', null=True, blank=True,
                                        on_delete=models.SET_NULL, verbose_name='默认地址')

    class Meta:
        db_table = 'tb_users'
        verbose_name = '用户'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username