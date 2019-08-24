from haystack import indexes

from .models import SKU


class SKUIndex(indexes.SearchIndex, indexes.Indexable):
    """SKU索引数据模型类"""
    text = indexes.CharField(document=True, use_template=True)

    def get_model(self):
        """返回建立索引的模型类"""
        return SKU

    def index_queryset(self, using=None):
        """返回要建立索引的数据查询集"""
        return self.get_model().objects.filter(is_launched=True)

# object --> SKU
# 手动生成初始索引--> python manage.py rebuild_index
# Indexing 16 商品SKU
# GET /meiduo/_mapping [status:404 request:0.014s]

