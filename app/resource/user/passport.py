from datetime import datetime, timedelta

from flask import current_app, g
from flask_restful import Resource
import random
from flask_restful.inputs import regex
from flask_restful.reqparse import RequestParser
from sqlalchemy.orm import load_only

from app import db, redis_cluster
from utils.constants import SMS_CODE_EXPIRE
from celery_tasks.sms.tasks import celery_send_sms_code
from utils.parser import mobile_type, username_type, pwd_type

from models.user import User
from utils.jwt_util import generate_jwt

from common.models.user import UserProfile
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
    路由：    post '/register/'
    业务逻辑； 验证数据，保存到数据库
    响应数据： json格式
        {
          "message": "ok",
          "data": {
            "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI",
            "userid": 1,
            "username": "xxssls01"    
          }
        }
"""


class LoginResource(Resource):
    """注册"""

    def post(self):
        # 获取参数
        parser = RequestParser()
        parser.add_argument('mobile', required=True, location='json', type=mobile_type)
        parser.add_argument('code', required=True, location='json', type=regex(r'^\d{6}$'), help='手机验证码错误')
        parser.add_argument('allow', required=True, location='json', type=str)

        args = parser.parse_args()
        mobile = args.mobile
        code = args.code
        if args.allow !='true':
            return {'message': 'Invalid allow', 'data': None}, 400


        # 校验短信验证码
        key = 'app:code:{}'.format(mobile)
        # real_code = redis_cluster.get(key)
        # if not real_code or real_code != code:
        #     return {'message': 'Invalid Code', 'data': None}, 400

        # 存入数据库
        # print('查询数据库')
        user = User.query.options(load_only(User.id)).filter(User.mobile == mobile).first()
        # print('查询结束')
        if user:
            user.last_login = datetime.now()
        else:
            print("数据库插入用户数据")
            user = User(mobile=mobile, name=mobile, last_login=datetime.now())
            userprofile = UserProfile()
            db.session.add(userprofile)
            # print("用户的id", user.id)
        # 存入数据库
        # input("等待")
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


