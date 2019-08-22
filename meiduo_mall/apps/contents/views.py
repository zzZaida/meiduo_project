from django.shortcuts import render
from django.views import View

from apps.goods.models import GoodsChannel


class IndexView(View):
    def get(self, request):

        categories = {}
        # 1.获取37个频道
        channels = GoodsChannel.objects.all()

        # 2.遍历37个频道
        for channel in channels:
            # 2.1 根据频道 获取频道id
            group_id = channel.group_id
            # 2.2 分组判断11组
            if not group_id in categories:
                categories[group_id] = {"channels": [], "sub_cats": []}

            # 3.从频道根据当前category_id获取一级分类
            cat1 = channel.category
            # 动态添加 url 属性
            cat1.url = channel.url
            categories[group_id]['channels'].append(cat1)

            # 4.二级分类 一级.subs.all()
            for cat2 in cat1.subs,all():
                cat2.sub_cats = []
                # 5.三级分类 二级.subs.all()
                for cat3 in cat2.subs.all():
                    cat2.sub_cats.append(cat3)

                categories[group_id]['sub_cats'].append(cat2)

        context = {
                    'categories': categories
                }

        return render(request, 'index.html', context)