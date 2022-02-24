import asyncio

from celery_tasks.main import celery_app

# from utils.req_weather import request_weather

@celery_app.task(name='celery_request__weather')
def celery_request_weather():
    print('定时地区请求 发送请求')
    # print(async_weather('北京'))

    # 创建一个新的loop对象
    # loop = asyncio.new_event_loop()
    # asyncio.set_event_loop(loop)
    #
    # try:
    #     # asyncio.gather()  # 收集响应
    #     rest = loop.run_until_complete(asyncio.gather(request_weather('北京')))
    #     print(rest)
    #     return rest[0]
    # finally:
    #     loop.close()


