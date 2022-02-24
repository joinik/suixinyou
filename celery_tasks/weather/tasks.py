import asyncio

from celery_tasks.main import celery_app

from utils.req2_wea import request_weather

@celery_app.task()
def celery_request_weather():
    print('定时地区请求 发送请求')
    request_weather('北京')

    # 创建一个新的loop对象


