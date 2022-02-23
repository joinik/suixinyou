from flask import g
from flask_restful import Resource
from flask_restful.reqparse import RequestParser
from sqlalchemy.orm import load_only

from app import db
from app.models.user import RouterCard
from common.utils.decorators import login_required
from common.utils.parser import action_parser


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

        # 模型类列表
        model_list = []
        for item in data:
            model_list.append(RouterCard(user_id=user_id,
                                         area_id=item.get("area_id"), arrive_time=item.get("arrive_time")))

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
        args = parser.parse_args()
        action = args.action
        user_id = g.user_id
        if action == 'do':
            router_list = RouterCard.query.options(load_only(RouterCard.id)). \
                filter(RouterCard.user_id == user_id, RouterCard.complete == True).all()

        elif action == 'no':
            router_list = RouterCard.query.options(load_only(RouterCard.id)). \
                filter(RouterCard.user_id == user_id, RouterCard.complete == 0).all()

        else:
            router_list = RouterCard.query.options(load_only(RouterCard.id)). \
                filter(RouterCard.user_id == user_id).all()

        rest = [
            {
                "area_id": item.area_id,
                "area": item.area.area_name,
                "comp_time": item.utime.isoformat(),
                "complete": item.complete
            } for item in router_list
        ]

        return {"message": "OK", "data": rest}


    def put(self):
        """修改行程是否完成"""

        # 1.根据area_id,user_id 查询用户的行程计划
        parser = RequestParser()
        parser.add_argument('area_id', required=True, location='json', type=int)

        # 1.1 获取参数
        args = parser.parse_args()
        area_id = args.area_id
        user_id = g.user_id

        # 2.修改行程计划为完成状态
        try:
            # 2.1 查询数据 根据area_id,user_id 查询用户的行程计划
            router_model = RouterCard.query.options(load_only(RouterCard.id)).filter(RouterCard.area_id == area_id,
                                                                      RouterCard.user_id == user_id).first()
            router_model.complete = 1

            db.session.add(router_model)
            db.session.commit()


        except Exception as e:
            print("行程 数据库, 查询失败")
            print(e)
            return {"message": "Invalid Access"}, 401


        # 3.返回响应
        return {"message": "OK", "data": None}

