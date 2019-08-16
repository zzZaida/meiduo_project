
from django.conf.urls import url
from django.contrib import admin

from . import views

urlpatterns = [

    url(r'^register', views.RegisterView.as_view()),

]
