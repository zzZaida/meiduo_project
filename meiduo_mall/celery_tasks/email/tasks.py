from celery_tasks.main import celery_app
# 使用django的settings获取配置项 将来 不用操心他加载是哪个配置文件(dev prod)
from django.conf import settings


@celery_app.task
def send_verify_email(email):

    from django.core.mail import send_mail

    subject = '美多商城验证邮箱'
    from_email = settings.EMAIL_FROM
    to_email = [email]
    html_message = "<a href='http://www.itcast.cn'>激活的链接</a>"

    send_mail(subject=subject, message='', from_email=from_email, recipient_list=to_email, html_message=html_message)