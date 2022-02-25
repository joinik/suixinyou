import asyncio

from celery_tasks.main import celery_app

from utils.req_weather import async_weather

@celery_app.task(name='celery_request__weather')
def celery_request_weather():
    print('定时地区请求 发送请求11111111')
    print(async_weather('北京'))
    print('结束celery 定时')



