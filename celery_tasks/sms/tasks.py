

from celery_tasks.main import celery_app

from common.utils.sms.SendMessage import Sms

@celery_app.task(name='celery_send_sms_code')
def celery_send_sms_code(moblie,code):
    print('容联云发送短信')
    Sms().send_message(moblie,(code,2))






