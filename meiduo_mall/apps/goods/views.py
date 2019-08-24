from django.shortcuts import render

# Create your views here.
from django.views import View


class ListView(View):
    def get(self, request, category_id, page_num):
        return render(request, 'list.html')