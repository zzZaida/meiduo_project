from django.shortcuts import render
from django.views import View

from apps.contents.utils import get_categories


class IndexView(View):
    def get(self, request):

        # 1. 获取三级分类商品 数据
        categories = get_categories()

        context = {
                    'categories': categories
                }

        return render(request, 'index.html', context)