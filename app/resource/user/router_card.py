import json
from datetime import datetime
from functools import reduce

from flask import g, request
from flask_restful import Resource
from flask_restful.reqparse import RequestParser
from sqlalchemy import or_
from sqlalchemy.orm import load_only

from app import db, redis_cluster
from app.models.area import Area
from app.models.user import RouterCard
from common.cache.weather import WeatherCache
from common.utils.decorators import login_required
from common.utils.parser import action_parser
from common.utils.req_ip import req_area
from common.utils.req_weather import async_weather


class TravelCardResource(Resource):
    """行程卡"""

    method_decorators = [login_required]

    def post(self):
        parser = RequestParser()
        parser.add_argument('data', required=True, location='json', type=dict, action='append', help='参数错误')
        # parser.add_argument('time', requi)

        args = parser.parse_args()
        # 获取参数
        data = args.data
        user_id = g.user_id
        # print(data)


        ''' 对list格式的dict进行去重'''

        def remove_list_dict_duplicate(data):
            run_function = lambda x, y: x if y in x else x + [y]
            return reduce(run_function, [[], ] + data)

        data = remove_list_dict_duplicate(data)
        # print(data)
        # input('等待')

        # 模型类列表
        model_list = []
        for item in data:
            try:
                # 先去 数据库查询，有的，就不添加了，
                if RouterCard.query.options(load_only(RouterCard.id)). \
                        filter(RouterCard.area_id == item.get("area_id"),
                               RouterCard.user_id == user_id,
                               RouterCard.arrive_time == item.get("arrive_time")).first():

                    # 跳过此次循环
                    continue

                else:
                    model_list.append(RouterCard(user_id=user_id,
                                                 area_id=item.get("area_id"),
                                                 arrive_time=item.get("arrive_time")))

            except Exception as e:
                # db.session.rollback()
                print("行程 查询重复数据 数据库失败，")
                print(e)
                return {"message": "以重复 添加", "data": None}, 401

        if not model_list:
            return {"message": "Invalid Access"}, 400

        try:
            # 进行数据库存储
            db.session.add_all(model_list)
            db.session.commit()
        except Exception as e:
            # db.session.rollback()
            print("行程 存入数据库失败，")
            print(e)
            return {"message": "系统繁忙，稍后再试", "data": None}, 401

        return {"message": "OK", "data": None}

    def get(self):
        parser = RequestParser()
        parser.add_argument('action', location='args', type=action_parser)

        # 获取参数
        # action = do 查询已完成的行程
        # action = no 查询未完成的行程
        # action = all 查询所有的行程

        args = parser.parse_args()
        action = args.action
        user_id = g.user_id
        try:
            if action == 'do':
                router_list = RouterCard.query.options(load_only(RouterCard.id)). \
                    filter(RouterCard.user_id == user_id, RouterCard.complete == True).all()

            elif action == 'no':
                router_list = RouterCard.query.options(load_only(RouterCard.id)). \
                    filter(RouterCard.user_id == user_id, RouterCard.complete == 0).all()

            else:
                router_list = RouterCard.query.options(load_only(RouterCard.id)). \
                    filter(RouterCard.user_id == user_id).all()

        except Exception as e:
            print('行程 查询数据库', )
            print(e)
            return {"message": "系统繁忙，稍后再试", "data": None}, 401
        rest = [
            item.to_dict() for item in router_list
        ]

        return {"message": "OK", "data": rest}

    def put(self):
        """修改行程是否完成"""

        # 1.根据area_id,user_id 查询用户的行程计划
        parser = RequestParser()
        parser.add_argument('area_id', required=True, location='json', type=int)
        parser.add_argument('arrive_time', required=True, location='json', type=str)
        parser.add_argument('new_area_id', required=True, location='json', type=int)
        parser.add_argument('new_arrive_time', required=True, location='json', type=str)
        parser.add_argument('action', location='json', type=str)

        # 1.1 获取参数
        args = parser.parse_args()
        area_id = args.area_id
        arrive_time = args.arrive_time
        new_area_id = args.new_area_id
        new_arrive_time = args.new_arrive_time
        action = args.action
        user_id = g.user_id

        if action == 'do':
            try:
                router_model = RouterCard.query.options(load_only(RouterCard.id)). \
                    filter(RouterCard.area_id == area_id,
                           RouterCard.user_id == user_id,
                           RouterCard.arrive_time == arrive_time).first()

                router_model.area_id = new_area_id
                router_model.arrive_time = new_arrive_time

                # 提交数据库
                db.session.add(router_model)
                db.session.commit()

                return {"message": "OK", "data": router_model.to_dict()}


            except Exception as e:
                print('修改行程 数据库 失败')
                print(e)
                return {"message": "Invalid Access"}, 400

        # 2.修改行程计划为完成状态
        try:
            # 2.1 查询数据 根据area_id,user_id 查询用户的行程计划
            router_model = RouterCard.query.options(load_only(RouterCard.id)). \
                filter(RouterCard.area_id == area_id,
                       RouterCard.user_id == user_id,
                       RouterCard.arrive_time == arrive_time).first()

            router_model.complete = 1

            db.session.add(router_model)
            db.session.commit()

            # 3.返回响应
            return {"message": "OK", "data": router_model.to_dict()}

        except Exception as e:
            print("行程 数据库, 查询失败")
            print(e)
            return {"message": "Invalid Access"}, 400



class WeatherResource(Resource):

    def get(self):
        ip = request.remote_addr
        city = req_area(ip)

        # print(city)
        # 根据前端发送的 用户地址信息

        area_model = None

        try:
            parser = RequestParser()
            parser.add_argument('city', location='args', type=str)
            args = parser.parse_args()
            # 获取请求参数
            city_code = args.city
            print('请求参数',city_code)

            if city_code:
                weather_cache = WeatherCache(areaid=city_code).get(city_code=city_code)

            else:
                # 1. 数据库查询 用户城市的文章信息
                area_model = Area.query.options(load_only(Area.id)). \
                    filter(or_(Area.area_name.like('%' + city + '%'),Area.id == city)).first()

                if not area_model:
                    return {"message": "111111111111  Invalid Access", "data": None}, 401

                weather_cache = WeatherCache(areaid=area_model.id).get(area_model=area_model)

            if not weather_cache:
                return {'message': "Invalid Weather_area", 'data': None}, 400

            return {'ip': ip, "area_id": area_model.id if area_model else city_code, "message": "OK",
                    "data": weather_cache}



        except Exception as e:
            print("地区查询 数据库，失败", )
            print(e)
            return {"message": "Invalid Access", "data": None}, 401




