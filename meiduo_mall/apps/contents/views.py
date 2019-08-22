from django.shortcuts import render
from django.views import View

from apps.contents.models import ContentCategory
from apps.contents.utils import get_categories


class IndexView(View):
    """首页广告"""
    def get(self, request):

        # 1.获取三级分类商品 数据
        categories = get_categories()

        # 2.获取广告数据
        contents = {}
        # 2.1 获取所有的 广告分类
        ad_categories = ContentCategory.objects.all()
        # 2.2 遍历分类 取出每个分类广告
        for category in ad_categories:
            contents[category.key] = category.content_set.filter(status=True).order_by('sequence')

        context = {
                    'categories': categories,
                    'contents': contents,
                }

        return render(request, 'index.html', context)