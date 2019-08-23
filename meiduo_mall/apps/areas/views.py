from django.http import JsonResponse
from django.shortcuts import render
from django.views import View

from apps.areas.models import Area
from utils.response_code import RETCODE


class AreasView(View):
    """
    SQL 省  select * from tb_areas where parent_id is NULL;
        市  select * from tb_areas where parent_id = 130000;
        县  select * from tb_areas where parent_id = 130100;

    ORM 省  Area.objects.filter(parent__isnull=True)
        市  Area.objects.filter(parent_id=area_id)
        县  Area.objects.filter(parent_id=area_id )

    """
    def get(self, request):

        # 1.接收参数
        area_id = request.GET.get('area_id')

        if not area_id:
            # 2.省的数据 area_id 为空
            province_model_list = Area.objects.filter(parent__isnull=True)

            # 将 ORM 的数据对象 转换成 给前端需要的 JSON 格式
            province_list = []
            for pro in province_model_list:
                province_list.append({'id': pro.id,'name': pro.name})

            return JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'province_list': province_list})
        else:
            # 3.市区的数据 area_id 有值
            # city_model_list = Area.objects.filter(parent_id=area_id)
            parent_model = Area.objects.get(id=area_id)  # 查询市或区的父级
            sub_model_list = parent_model.subs.all()

            # 将 ORM 的数据对象 转换成 给前端需要的 JSON 格式
            subs_list = []
            for city in sub_model_list:
                subs_list.append({'id': city.id, 'name': city.name})

            sub_data = {
                'id': parent_model.id,
                'name': parent_model.name,
                'subs': subs_list
            }

            return JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'sub_data': sub_data})



