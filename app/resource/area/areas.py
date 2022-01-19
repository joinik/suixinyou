from flask import g
from flask_restful import Resource
from flask_restful.reqparse import RequestParser
from sqlalchemy.orm import load_only

from app import db, redis_cluster
from app.models.user import Article, ArticleContent, User, Area

from common.utils.decorators import login_required





"""
查询省份数据
前端：用户选择省份或者市 发送请求， 获取下一级信息
后端；
    请求      传递省份，或者市的id
    逻辑      根据id 查area对象，获取下一级信息，转为字典数据
    返回响应; json
    


"""


class AreaProvinceResource(Resource):

    def get(self):
        """提供省份数据"""

        # 查询缓存，里面是否有 省份 数据
        if redis_cluster.get('province_list'):
            print('---------->>>>>>>>>省份缓存')
            return {'province_list': eval(redis_cluster.get('province_list'))}

        else:
            try:
                province_model_list = Area.query.options(load_only(Area.id)).filter(Area.parent_id == 0).all()
                # print(province_model_list)
                # input("等待")

                # 序列化数据
                province_list = []
                for item in province_model_list:
                    province_list.append({"area_id": item.id, "area_name": item.area_name})

            except Exception as e:
                print("省份数据查询错误")
                print(e)
                return {'message': '省份数据错误', "data": None}, 400

            redis_cluster.set('province_list', province_list, 3600)
            return {'province_list': province_list}



class SubsResource(Resource):

    def get(self, pk):

        # 查询redis集群缓存
        if redis_cluster.get("sub_data_" + str(pk)):
            print(">>>>>>>>>>>>subs缓存")
            return {'sub_data': eval(redis_cluster.get("sub_data_" + str(pk)))}
        else:
            try:
                parent_model = Area.query.options(load_only(Area.id)).filter(Area.id == pk).first()
                # print(parent_model, "省份数据")
                # 序列化数据
                sub_model_list = parent_model.subs.all()
                # print(sub_model_list)
                if len(sub_model_list) ==1:
                    sub_model_list = sub_model_list[0].subs.all()

                subs = []
                for item in sub_model_list:
                    subs.append({"area_id": item.id, "area_name": item.area_name})


            except Exception as e:
                print("subs数据查询错误")
                print(e)
                return {'message': 'subs数据错误', "data": None}, 400

            redis_cluster.set("sub_data_" + str(pk), subs, 3600)
            return {"sub_data": subs}

















