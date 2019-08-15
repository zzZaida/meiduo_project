#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":

    # 测试环境的配置文件  os 系统库  environ   setdefault设置默认
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "meiduo_mall.settings.development")

    # 生产环境 配置文件
    # os.environ.setdefault("DJANGO_SETTINGS_MODULE", "meiduo_mall.settings.product")

    try:
        from django.core.management import execute_from_command_line
    except ImportError:
        # The above import may fail for some other reason. Ensure that the
        # issue is really that Django is missing to avoid masking other
        # exceptions on Python 2.
        try:
            import django
        except ImportError:
            raise ImportError(
                "Couldn't import Django. Are you sure it's installed and "
                "available on your PYTHONPATH environment variable? Did you "
                "forget to activate a virtual environment?"
            )
        raise
    execute_from_command_line(sys.argv)