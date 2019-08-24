from django import http
from django.shortcuts import render

# Create your views here.
from django.views import View


from apps.contents.utils import get_categories
from apps.goods.models import SKU, GoodsCategory
from apps.goods.utils import get_breadcrumb
from apps.verifications import contants
from utils.response_code import RETCODE


class ListView(View):
    """商品列表页"""
    def get(self, request, category_id, page_num):
        # category_id 三级分类ID

        # 1.三级分类 调用 contents 封装好的代码
        categories = get_categories()

        # 2.面包屑组件 cat3.parent
        # 获取cat3对象
        cat3 = GoodsCategory.objects.get(id=category_id)
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


class HotGoodsView(View):
    """商品热销排行"""
    def get(self, request, category_id):
        # 5.热销商品
        # 5.1 根据销量 排序
        hot_skus = SKU.objects.filter(category=category_id, is_launched=True).order_by('-sales')
        # 5.2 取前两个
        hot_skus = hot_skus[:2]
        # 5.3 返回给前端需要的格式 [{ }]
        hot_list = []
        for sku in hot_skus:
            hot_list.append({
                'id': sku.id,
                'default_image_url': sku.default_image.url,
                'name': sku.name,
                'price': sku.price
            })
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'hot_skus': hot_list})


class DetailView(View):
    """商品详情页"""
    def get(self, request, sku_id):
        """提供商品详情页"""
        # 获取当前sku的信息
        try:
            sku = SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return render(request, '404.html')

        # 查询商品频道分类
        categories = get_categories()
        # 查询面包屑导航  n:1-->sku.外键属性
        breadcrumb = get_breadcrumb(sku.category)

        # 构建当前商品的规格键
        sku_specs = sku.specs.order_by('spec_id')
        sku_key = []
        for spec in sku_specs:
            sku_key.append(spec.option.id)
        # 获取当前商品的所有SKU   n:1-->sku.外键属性
        skus = sku.spu.sku_set.all()
        # 构建不同规格参数（选项）的sku字典
        spec_sku_map = {}
        for s in skus:
            # 获取sku的规格参数
            s_specs = s.specs.order_by('spec_id')
            # 用于形成规格参数-sku字典的键
            key = []
            for spec in s_specs:
                key.append(spec.option.id)
            # 向规格参数-sku字典添加记录
            spec_sku_map[tuple(key)] = s.id
        # 获取当前商品的规格信息
        goods_specs = sku.spu.specs.order_by('id')
        # 若当前sku的规格信息不完整，则不再继续
        if len(sku_key) < len(goods_specs):
            return
        for index, spec in enumerate(goods_specs):
            # 复制当前sku的规格键
            key = sku_key[:]
            # 该规格的选项
            spec_options = spec.options.all()
            for option in spec_options:
                # 在规格参数sku字典中查找符合当前规格的sku
                key[index] = option.id
                option.sku_id = spec_sku_map.get(tuple(key))
            spec.spec_options = spec_options

        # 渲染页面
        context = {
            'categories': categories,
            'breadcrumb': breadcrumb,
            'sku': sku,
            'specs': goods_specs,
        }
        return render(request, 'detail.html', context)