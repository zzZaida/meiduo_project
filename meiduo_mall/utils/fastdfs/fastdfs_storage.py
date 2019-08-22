from django.conf import settings
from django.core.files.storage import Storage


class FastDFSStorage(Storage):

    def __init__(self):
        self.base_url = settings.FDFS_BASE_URL

    # 必写函数
    def _open(self, name, mode='rb'):
        pass
    def _save(self, name, content, max_length=None):
        pass

    # 重写父类的 url 函数 返回一个IP:port/00/00/meizi.png
# http://192.168.88.133:8888/  +  group1/M00/00/00/wKhYhV1eRXSAS8lkAACKZoFLFKk996.jpg
    def url(self, name):
        return self.base_url + name