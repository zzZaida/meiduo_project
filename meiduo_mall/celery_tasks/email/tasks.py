from celery_tasks.main import celery_app
# 使用django的settings获取配置项 将来 不用操心他加载是哪个配置文件(dev prod)
from django.conf import settings

# bind=True --> r任务当做对象 self
# bind:保证task对象会作为第一个参数自动传入
# name:异步任务别名
# retry_backoff:异常自动重试的时间间隔 第n次(retry_backoff*2^(n-1))s
# max_retries:异常自动重试次数的上限
# 将来 发邮件 发短信 一次失败了,多次自动尝试发送; 可以设置重试的次数 间隔时间


@celery_app.task(bind=True, name='send_verify_email', retry_backoff=3)
def send_verify_email(self,to_email, verify_url):

    from django.core.mail import send_mail

    subject = '美多商城验证邮箱'
    from_email = settings.EMAIL_FROM
    to_email = [to_email]
    html_message = '<p>尊敬的用户您好！</p>' \
                   '<p>感谢您使用美多商城。</p>' \
                   '<p>您的邮箱为：%s 。请点击此链接激活您的邮箱：</p>' \
                   '<p><a href="%s">%s<a></p>' % (to_email, verify_url, verify_url)

    try:
        send_mail(subject=subject, message='', from_email=from_email, recipient_list=to_email,
                  html_message=html_message)
    except Exception as e:
        # 有异常自动重试三次
        raise self.retry(exc=e, max_retries=3)