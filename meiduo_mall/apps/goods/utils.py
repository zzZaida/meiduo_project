

# 1.面包屑组件的数据
def get_breadcrumb(cat3):

    # 1 使用cat3-->cat2
    cat2 = cat3.parent

    # 2 cat2-->cat1
    cat1 = cat2.parent

    # 因为前端需要url属性-->而三级分类表 只有id,name,parent字段-->动态添加url
    # 频道组--频道表(group_id,category_id,url)<--分类表
    # 分类表--频道表-- cat1.goodschannel_set.all()
    # 频道表--多个频道--多个url-->只有第一个频道 设置url-->all()[0].url
    cat1.url = cat1.goodschannel_set.all()[0].url

    # 3 返回数据
    breadcrumb = {
        'cat1':cat1,
        'cat2':cat2,
        'cat3':cat3,

    }

    return breadcrumb