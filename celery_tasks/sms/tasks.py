# -*- coding: utf-8 -*-
# author: JK time:2021/12/24

from celery_tasks.main import celery_app
from celery import Celery
from common.utils.sms.SendMessage import Sms

# celery_app = Celery('suixinyouTravel', broker='redis://127.0.0.1:6381/15')


@celery_app.task(name='celery_send_sms_code')
def celery_send_sms_code(moblie,code):
    print('容联云发送短信')
    Sms().send_message(moblie,(code,2))






