from django.shortcuts import render

# Create your views here.
from django.views import View

from apps.contents.models import ContentCategory
from apps.contents.utils import get_categories
from apps.goods.models import SKU
from apps.goods.utils import get_breadcrumb
from apps.verifications import contants


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
        from django.core.paginator import Paginator
        # 4.1 一页显示几个
        paginator = Paginator(skus, contants.GOODS_LIST_LIMIT)
        # 4.2 总页数
        all_pages = paginator.num_pages
        # 4.3 当前页 显示的内容
        page_skus = paginator.page(page_num)

        # 5.热销商品

        context = {
            'categories': categories,  # 频道分类
            'breadcrumb': bread_crumb,  # 面包屑导航
            'sort': sort,  # 排序字段
            'category': cat3,  # 第三级分类
            'page_skus': page_skus,  # 分页后数据
            'total_page': all_pages,  # 总页数
            'page_num': page_num,  # 当前页码
        }

        return render(request, 'list.html', context)