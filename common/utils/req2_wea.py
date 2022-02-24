import httpx


def request_weather(area_name):
    try:
        resp = httpx.get("http://wthrcdn.etouch.cn/weather_mini?city={}".format(area_name))
        assert resp.status_code == 200
        print('天气返回响应')
        html = resp.json()
        # print(html)
        # input('等待》》》》')
        return html

    except Exception as e:
        print('天气接口 异常')
        print(e)
        return {"message": "天气 查询 繁忙，稍后再试", "data": None}

