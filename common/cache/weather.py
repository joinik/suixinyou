# ORM: 用面向对象的形式进行数据的增删改查
# ORM: 表->类  记录->对象
# redis缓存层:   数据对象/数据集合 -> 类   redis数据 -> 对象

import json

from sqlalchemy import or_
from sqlalchemy.orm import load_only
from app import redis_cluster
from app.models.area import Area
from app.models.user import User


# user:<用户id>:basic   hash   {'name': xx, 'mobile': xx}

# 用户数据缓存类
# 属性
#    userid   用户id
# 方法
#    get()    获取缓存数据
#    clear()  删除缓存数据
from common.utils.constants import UserCacheTTL, UserNotExistTTL, WeatherCacheTTL
from common.utils.req_weather import async_weather


class WeatherCache:
    """地区天气文章 数据缓存类"""

    def __init__(self, areaid):

        self.areaid = areaid  # areaid 地区id
        self.key = 'area:{}:weather:'.format(self.areaid)  # redis的键

    def get(self, area_model=None, city_code=None):
        """获取数据"""
        # 先从缓存中读取数据
        data = redis_cluster.hgetall(self.key)  # 键不存在返回空字典

        if data:  # 如果有, 再判断是否为默认值

            if data.get('null'):
                # 如果为默认值, 则返回None
                return None
            else:
                # 如果不为默认值, 则返回数据
                print('获取用户天气地区缓存数据')
                # print(type(data))
                data["weather"] = eval(data.get('weather'))
                data["area_article"] = eval(data.get('area_article'))
                return data

        else:  # 如果没有, 再从数据库中读取数据
            if city_code:
                # 查询数据库
                area_model = Area.query.options(load_only(Area.id)). \
                    filter(or_(Area.area_name.like('%' + city_code + '%'), Area.id == city_code)).first()

            # 判断数据库中的是否有此地区的数据
            if area_model:

                # 封装 地区的 文章详情
                area_article = []
                # 1.1 数据序列化
                gonggao = []  # 公告列表
                huati = []  # 话题列表
                qiuzhu = []  # 求助列表
                huodong = []  # 活动列表
                youji = []  # 游记列表
                business = []  # 商家列表
                for item in area_model.articles.all():
                    if item.category.cate_name == '公告' and item.status == 2:
                        if len(gonggao) == 10:
                            continue
                        gonggao.append(item.todict())
                    elif item.category.cate_name == '话题' and item.status == 2:
                        if len(huati) == 10:
                            continue
                        huati.append(item.todict())
                    elif item.category.cate_name == '求助' and item.status == 2:
                        if len(qiuzhu) == 10:
                            continue
                        qiuzhu.append(item.todict())
                    elif item.category.cate_name == '活动' and item.status == 2:
                        if len(huodong) == 10:
                            continue
                        huodong.append(item.todict())
                    elif item.category.cate_name == '游记' and item.status == 2:
                        if len(youji) == 10:
                            continue
                        youji.append(item.todict())
                    elif item.category.cate_name == '商家' and item.status == 2:
                        if len(business) == 10:
                            continue
                        business.append(item.todict())

                # area_article['公告'] = gonggao
                # area_article['话题'] =  huati
                # area_article['求助'] = qiuzhu
                # area_article['活动'] =  huodong
                # area_article['游记'] = youji
                # area_article['商家'] =  business

                # 更新 为列表嵌套
                area_article.append({'公告': gonggao})
                area_article.append({'话题': huati})
                area_article.append({'求助': qiuzhu})
                area_article.append({'活动': huodong})
                area_article.append({'游记': youji})
                area_article.append({'商家': business})

                # 查询redis集群中 天气 缓存
                area_name = area_model.area_name
                print('城市名字', area_name)


                # input('等待')

                print("weather 天气查询中")
                # 2. 进行天气查询
                html = async_weather(area_name)
                # 进行天气数据缓存


                weather_dict = {"area_article": area_article, "weather": html}

                redis_cluster.hmset(self.key, weather_dict)
                redis_cluster.expire(self.key, 3600 * 6)  # 缓存时间 6小时
                print('进行天气数据缓存,并回填')

                return weather_dict


            else:  # 如果数据库没有, 在缓存中设置默认值-1, 然后返回None

                # 设置默认值(防止缓存穿透)
                redis_cluster.hmset(self.key, {'null': 1})
                redis_cluster.expire(self.key, 60 * 10)
                return None


    def clear(self):
        """删除缓存数据"""
        redis_cluster.delete(self.key)
