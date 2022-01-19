# -*- coding: utf-8 -*-
# author: JK time:2021/12/22
import random

EXTRA_ENV_CONFIG = 'ENV_CONFIG'     #额外配置对应的环境变量名

SMS_CODE_EXPIRE = 300  # 短信验证码有效期

BASE_URL_PRIFIX = '/app'  # 基础URL的前缀


# 升级2: 将过期时间处理封装为类
class BaseCacheTTL:
    """过期时间基类"""
    TTL = 60 * 10  # 过期时间
    MAX_DELTA = 60  # 最大随机值

    @classmethod
    def get_val(cls):
        """获取过期时间"""
        return cls.TTL + random.randint(0, cls.MAX_DELTA)


class UserCacheTTL(BaseCacheTTL):
    """用户缓存过期时间类"""
    TTL = 60 * 60 * 2  # 过期时间
    MAX_DELTA = 600  # 最大随机值

class UserNotExistTTL(BaseCacheTTL):
    """用户不存在过期时间类"""
    pass






