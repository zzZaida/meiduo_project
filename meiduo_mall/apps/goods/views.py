from django.shortcuts import render

# Create your views here.
from django.views import View

from apps.contents.models import ContentCategory
from apps.contents.utils import get_categories


class ListView(View):
    """商品列表页"""
    def get(self, request, category_id, page_num):
        # category_id 三级分类ID

        # 1.三级分类 调用 contents 封装好的代码
        categories = get_categories()

        # 2.面包屑组件 cat3.parent
        # 获取cat3对象
        cat3 = ContentCategory.objects.get(id=category_id)
        bread_crumb = get_categories(cat3)

        # 3.排序
        # 4.分页器--paginator
        # 5.热销商品

        context = {
            'categories': categories,
            'breadcrumb': bread_crumb
        }

        return render(request, 'list.html', context)