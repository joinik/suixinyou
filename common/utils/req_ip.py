import httpx


def req_area(ip):
    #  通过ip 获取 地理位置

    resp = httpx.get('https://restapi.amap.com/v5/ip?key={}&type=4&ip={}'.format(key, ip))
    assert resp.status_code == 200
    resp = resp.json()
    city = resp.get('city', '宿迁市')
    return city
