



from flask import request, g
from utils.jwt_util import verify_jwt

from common.utils.req_ip import req_area


def get_userinfo():
    """获取用户信息"""

    # 根据 请求ip，查询物理ip地址
    ip = request.remote_addr
    city = req_area(ip)
    g.city = city

    # 获取请求头中的token
    auth = request.headers.get('Authorization')
    g.user_id = None     # 如果未登录， userid=None
    g.is_refresh = None       # 设置是否刷新token
    if auth and auth.startswith('Bearer '):
        "提取token 0-6 被Bearer和空格占用 取下标7以后的所有字符"
        token = auth[7:]
        # 校验token
        data = verify_jwt(token)

        if data:    # 校验成功
            g.user_id = data.get('user_id')   # 如果已登录，  userid=2
            g.is_refresh = data.get('is_refresh')





