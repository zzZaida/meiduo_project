
from django.conf.urls import url
from django.contrib import admin

from . import views

urlpatterns = [

    # 4.图片验证码 image_codes/(?P<uuid>[\w-]+)/
    url(r'^image_codes/(?P<uuid>[\w-]+)/$', views.ImageCodeView.as_view()),

    # 5.短信验证码 /sms_codes/(?P<mobile>1[3-9]\d{9})/
    url(r'^sms_codes/(?P<mobile>1[3-9]\d{9})/$', views.SMSCodeView.as_view()),

]
