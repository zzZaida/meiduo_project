
from celery_tasks.main import celery_app
@celery_app.task
def ccp_send_sms_code(mobile, sms_code):
    # 5.发送短信-- 第三方联容云--
    from libs.yuntongxun.sms import CCP
    #  CCP().send_template_sms('手机号', ['验证码', '过期时间5分钟'], 短信模板1)
    result = CCP().send_template_sms(mobile, [sms_code, 5], 1)
    print("当前验证码是:", sms_code)

    return result