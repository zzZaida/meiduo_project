import os

from django.conf import settings

from apps.contents.models import ContentCategory
from apps.contents.utils import get_categories
from django.template import loader


def generate_static_index_html():
    """
    生成静态的主页html文件
    """

    # <1> 获取首页需要的 数据库数据
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

    # <2> 获取 index 模板文件  loader加载
    # from django.template import loader
    template = loader.get_template('index.html')

    # <3> 渲染数据到模板文件 ==> html_text(渲染完毕的纯字符串)
    html_text = template.render(context)

    # <4> 将html_text 写入到本地文件
    file_path = os.path.join(settings.STATICFILES_DIRS[0], 'index.html')

    with open(file_path, 'w')as f:
        f.write(html_text)

# 广告商没钱了  过节--重新生成首页--定时任务crontab静态化首页--dev.py

# 验证
# python manage.py shell
# >>> from apps.contents.crons import generate_static_index_html
# >>> generate_static_index_html()


# 开启测试静态服务器
# python -m http.server 8080 --bind 127.0.0.1