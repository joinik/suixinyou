import json
from datetime import datetime, timedelta

import requests
from flask import current_app, g
from flask_restful import Resource
import random
from flask_restful.inputs import regex
from flask_restful.reqparse import RequestParser
from sqlalchemy.orm import load_only

from app import db, redis_cluster
from utils.constants import SMS_CODE_EXPIRE

from app.models.area import Area
from celery_tasks.sms.tasks import celery_send_sms_code
from utils.parser import mobile_type, username_type, pwd_type

from app.models.user import User, UserProfile

from common.utils.jwt_util import _generate_tokens

"""
前端  用户输入手机号 点击获取短信验证码， 发送axiou请求  手机号
GET    /sms/codes/15532272912
    

后端 
    接收请求：  参数  1，手机号
    业务逻辑：  验证手机号，生成短信验证码， 存入redis 数据库，  celery 发送短信功能
    响应数据：  json 格式
        
        {
          "message": "ok",
          "data": {
            "mobile": 135xxxxxxxx    
          }
        }
"""


class SMSCodeResource(Resource):
    """获取短信验证码"""

    def get(self, mobile):
        # 随机生成短信验证码
        rand_num = '%06d' % random.randint(0, 999999)
        key = 'app:code:{}'.format(mobile)
        redis_cluster.set(key, rand_num, ex=SMS_CODE_EXPIRE)

        # celery 第三方发送短信
        # celery_send_sms_code.delay(mobile, rand_num)
        print('>>>>>异步发送短信')
        print('短信验证码： "mobile": {}, "code": {}'.format(mobile, rand_num))
        return {'mobile': mobile}


"""
手机号验证
前端：用户输入手机号，失去焦点，发送一个axios请求
后端：
    接受请求：接收手机号
    业务逻辑：根据手机号查询数据库，是否已经注册
    路由：    get /mobiles/<mob:mobile>
    响应：    json格式
            {"errno": 0, "message": "手机号可以使用"}
        
"""


class MobileResource(Resource):
    def get(self, mobile):
        # print("手机号", mobile)
        # 根据手机号查询数据库 是否已经注册了
        if User.query.options(load_only(User.id)).filter(User.mobile == mobile).first():
            return {"errno": 1002, "message": "手机号已经注册..."}

        return {"errno": 0, "message": "手机号可以使用"}


"""
注册
前端： 用户输入，用户名，密码，确认密码，短信验证码，同意协议，点击注册按钮，发送axios请求

后端：
    接收请求：接收json数据
    路由：    post 'app/authorizations'
    业务逻辑； 验证数据，保存到数据库
    响应数据： json格式
        {
          "message": "ok",
          "data": {
            "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI",
            "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGci" 
          }
        }
"""


class LoginResource(Resource):
    """注册"""

    def get_openid(self,user_code):
        result = requests.get(
            'https://api.weixin.qq.com/sns/jscode2session?appid=&secret=&js_code={}&grant_type=authorization_code'.format(
                user_code))
        return json.loads(result.text)

    def post(self):
        # 获取参数
        parser = RequestParser()
        parser.add_argument('mobile', location='json', type=mobile_type)
        parser.add_argument('vcode', location='json', type=regex(r'^\d{6}$'), help='手机验证码错误')
        parser.add_argument('nick_name', location='json', type=regex(r'\S{3,10}'), help="昵称格式错误")
        parser.add_argument('allow', location='json', type=str)
        parser.add_argument("wxcode", location="json", type=str)

        args = parser.parse_args()
        mobile = args.mobile
        vcode = args.vcode
        wxcode = args.wxcode
        nick_name = args.nick_name
        print("用户昵称,",nick_name)


        # 微信方式登录
        if wxcode:
            # 调用微信登录 换取凭证
            req_info = self.get_openid(user_code=wxcode)
            print(req_info)
            input("微信接口返回的数据")

        if args.allow != 'true':
            return {'message': 'Invalid allow', 'data': None}, 400

        # 校验短信验证码
        # key = 'app:code:{}'.format(mobile)
        # real_code = redis_cluster.get(key)
        # if not real_code or real_code != vcode:
        #     return {'message': 'Invalid Code', 'data': None}, 400

        # 存入数据库
        # print('查询数据库')
        user = User.query.options(load_only(User.id)).filter(User.mobile == mobile).first()
        # print(user)
        # print('查询结束')
        if user:
            user.last_login = datetime.now()
        else:
            try:
                # 进行用户名查询，存在，就不让存储数据了
                if User.query.options(load_only(User.id)).filter(User.name == nick_name).first():
                    return  {"message": "用户名重复", "data": None}, 400

                print("数据库插入用户数据")
                user = User(mobile=mobile, name=nick_name, last_login=datetime.now())

                city = g.city
            except Exception as e:
                print("地区查询 数据库，失败", )
                print(e)
                return {"message": "Invalid Access", "data": None}, 401


            try:
                # 1. 数据库查询 用户城市的文章信息
                area_model = Area.query.options(load_only(Area.id)).filter(
                    Area.area_name.like('%' + city + '%')).first()
            except Exception as e:
                print("地区查询 数据库，失败", )
                print(e)
                return {"message": "Invalid Access", "data": None}, 401

            user.last_area_id = area_model.id

            db.session.add(user)
            # 先插入数据，才能拿到user的id
            db.session.flush()
            print("用户的id", user.id)

            userprofile = UserProfile(user_id=user.id)
            db.session.add(userprofile)
            db.session.commit()

        # 存入数据库
        db.session.add(user)
        db.session.commit()

        # 生成jwt
        token, refresh_token = _generate_tokens(user.id)
        return {'token': token, 'refresh_token': refresh_token}, 201

    def put(self):
        if g.is_refresh:
            token, refresh_token = _generate_tokens(g.user_id, False)
            return {'token': token}, 201
        else:
            return {'message': "Invalid refreshToken", 'data': None}, 403


"""
获取用户信息

请求方式    
GET

请求头
Authorization    用户token

响应数据  json
{
    "message": "OK",
    "data": {
        "id": 1155,
        "name": "18912323424",
         "photo": "xxxxx",
        "intro": "xxx",
        "dianzan_count": 0,
        "travel_note_count": 0,
        "dianliang_area_count": 0
    }
}

"""
