import base64
import pickle


class CookieSecret(object):
    # 加密
    @classmethod
    def dumps(cls, data):

        # 1. 将需要加密 data-->bytes 为了保证解码的时候 原始数据格式不变
        data_bytes = pickle.dumps(data)

        # 2.64加密 对bytes进行加密
        base64_data = base64.b64encode(data_bytes)

        # 3.转成str-->cookie(k,v)需要字符串
        base64_str = base64_data.decode()
        return base64_str

    # 解密
    @classmethod
    def loads(cls, data):
        # 1.解密
        decode_data = base64.b64decode(data)

        # 2.回退到原始的数据格式
        data_pickle = pickle.loads(decode_data)
        return data_pickle