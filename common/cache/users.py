# ORM: 用面向对象的形式进行数据的增删改查
# ORM: 表->类  记录->对象
# redis缓存层:   数据对象/数据集合 -> 类   redis数据 -> 对象

import json
from sqlalchemy.orm import load_only
from app import redis_cluster
from app.models.user import User


# user:<用户id>:basic   hash   {'name': xx, 'mobile': xx}

# 用户数据缓存类
# 属性
#    userid   用户id
# 方法
#    get()    获取缓存数据
#    clear()  删除缓存数据
from common.utils.constants import UserCacheTTL, UserNotExistTTL


class UserCache:
    """用户数据缓存类"""

    def __init__(self, userid):
        self.userid = userid  # 用户id
        self.key = 'user:{}:basic'.format(self.userid)  # redis的键

    def get(self):
        """获取数据"""
        # 先从缓存中读取数据
        data = redis_cluster.hgetall(self.key)  # 键不存在返回空字典

        if data:  # 如果有, 再判断是否为默认值

            if data.get('null'):
                # 如果为默认值, 则返回None
                return None
            else:
                # 如果不为默认值, 则返回数据
                print('获取用户缓存数据')
                return data

        else:  # 如果没有, 再从数据库中读取数据

            # 查询数据库
            user = User.query.options(
                load_only(User.id, User.name, User.profile_photo, User.introduction, User.travel_note_num,
                          User.dianzan_num, User.dianliang_area_num, User.business, User.last_address.area_name)).filter(User.id == self.userid).first()

            if user:  # 如果数据库有, 将数据回填到缓存中, 然后返回数据

                user_dict = user.to_dict()
                # 回填数据到缓存中
                redis_cluster.hmset(self.key, user_dict)
                redis_cluster.expire(self.key,  UserCacheTTL.get_val())
                print('查询用户数据并回填')
                return user_dict

            else:  # 如果数据库没有, 在缓存中设置默认值-1, 然后返回None

                # 设置默认值(防止缓存穿透)
                redis_cluster.hmset(self.key, {'null': 1})
                redis_cluster.expire(self.key, UserNotExistTTL.get_val())
                return None


    def clear(self):
        """删除缓存数据"""
        redis_cluster.delete(self.key)
