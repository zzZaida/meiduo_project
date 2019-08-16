from django.shortcuts import render

from django.views import View


class RegisterView(View):
    # 1 注册页面显示
    def get(self,request):

        return render(request, 'register.html')