from django.shortcuts import render

# Create your views here.
from django.views import View

from apps.contents.models import ContentCategory
from apps.contents.utils import get_categories
from apps.goods.models import SKU
from apps.goods.utils import get_breadcrumb


class ListView(View):
    """商品列表页"""
    def get(self, request, category_id, page_num):
        # category_id 三级分类ID

        # 1.三级分类 调用 contents 封装好的代码
        categories = get_categories()

        # 2.面包屑组件 cat3.parent
        # 获取cat3对象
        cat3 = ContentCategory.objects.get(id=category_id)
        bread_crumb = get_breadcrumb(cat3)

        # 3.排序  按照排序规则查询该分类商品SKU信息
        # 3.1 sort == 'price':前端传入参数 hot default 不能直接对接数据库
        sort = request.GET.get('sort')
        if sort == 'price':
            order_field = 'price'
        elif sort == 'hot':
            order_field = '-sales'
        else:
            order_field = 'create_time'
        # 3.2 SKU.objects.filter().order_by()
        skus = SKU.objects.filter(category=cat3, is_launched=True).order_by(order_field)
        print(skus)

        # 4.分页器--paginator
        # 5.热销商品

        context = {
            'categories': categories,
            'breadcrumb': bread_crumb
        }

        return render(request, 'list.html', context)