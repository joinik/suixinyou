import asyncio

import httpx
from flask import jsonify

from app import redis_cluster


def async_weather(area_name):
    async def request_weather(area_name):


        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get("http://wthrcdn.etouch.cn/weather_mini?city={}".format(area_name))
                assert resp.status_code == 200
                print('天气返回响应')
                html = resp.json()
                print(type(html))
                print(resp)
                # input('等待》》》》')
                return html

        except Exception as e:
            print('天气接口 异常')
            print(e)
            return {"message": "天气 查询 繁忙，稍后再试", "data": None}


    # 创建一个新的loop对象
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        # asyncio.gather()  # 收集响应
        rest = loop.run_until_complete(asyncio.gather(request_weather(area_name)))
        return rest[0]
    finally:
        loop.close()






