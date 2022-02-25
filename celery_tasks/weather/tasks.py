import asyncio

from celery_tasks.main import celery_app


from utils.req_weather import async_weather
@celery_app.task()
def celery_request_weather():
    print('定时地区请求 发送请求')
    html = async_weather('北京')
    print(html)
    print('结束celery 定时')
    # 创建一个新的loop对象


