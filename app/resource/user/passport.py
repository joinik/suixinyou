# -*- coding: utf-8 -*-
# author: JK time:2021/12/24


from flask_restful import Resource
import random
from app import redis_client
from utils.constants import SMS_CODE_EXPIRE
from celery_tasks.sms.tasks import celery_send_sms_code

class SMSCodeResource(Resource):
    """获取短信验证码"""
    def get(self, mobile):
        #
        rand_num = '%06d' % random.randint(0, 999999)

        key = 'app:code:{}'.format(mobile)
        redis_client.set(key, rand_num, ex=SMS_CODE_EXPIRE)

        # celery 第三方发送短信
        celery_send_sms_code.delay(mobile,rand_num)
        print('>>>>>异步发送短信')
        print('短信验证码： "mobile": {}, "code": {}'.format(mobile, rand_num))
        return {'mobile': mobile}


