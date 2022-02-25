import httpx


def req_area(ip):
    #  通过ip 获取 地理位置
    resp = httpx.get('https://restapi.amap.com/v5/ip?key=677f025efeda715a72a7837f85f576f9&type=4&ip={}'.format(ip))
    resp = resp.json()
    city = resp.get('city', '宿迁市')
    return city