from flask import g
from flask_restful import Resource
from flask_restful.reqparse import RequestParser
from sqlalchemy.orm import load_only

from utils.decorators import login_required

from app.models.user import User, UserProfile

from utils.parser import image_file

from app import db
from common.cache.users import UserCache
from common.utils.img_storage import upload_file
from common.utils.parser import username_type, email_type

"""
获取用户基本信息

请求方式
GET

请求头
Authorization    用户token

响应数据  json  200
{
    "message": "OK",
    "data": {
        "id": 1,
        "name": "dsf12123",
        "photo": null,
        "intro": "顶峰就是加肥加大so的设计费级第四节放的数据就",
        "dianzan_count": 0,
        "travel_note_count": 0,
        "dianliang_area_count": 0,
        "business": 0,
        "last_address": null
    }
}

错误响应 401
{ 
    "message": "Invalid Token",
    "data": null
}


"""


class CurrentUserResource(Resource):
    """个人中心-当前用户"""
    method_decorators = {'get': [login_required]}
    def get(self):
        userid = g.user_id

        # 查询用户数据
        # user = User.query.options(load_only(User.id))\
        #     .filter(User.id == userid).first()

        user_cache = UserCache(userid).get()
        if user_cache:
            return user_cache
        else:
            return {'message': "Invalid User", 'data': None}, 400


"""
获取用户个人信息

请求方式
GET

请求头
Authorization    用户token

响应数据  json  200
{
    "message": "OK",
    "data": {
        "id": 1,
        "name": "dsf12123",
        "email": "fdsfd@168.com",
        "gender": "MAN",
        "age": 123,
        "default_address": null
    }
}

错误响应 401
{ 
    "message": "Invalid Token",
    "data": null
}


"""




class UserInfoResource(Resource):
    """查询用户个人信息"""
    method_decorators = {'get': [login_required], 'put': [login_required]}

    def get(self):
        userid = g.user_id

        # 查询用户数据
        user = UserProfile.query.options(load_only(UserProfile.user_id)) \
            .filter(UserProfile.user_id == userid).first()

        return user.to_dict()

    def put(self):
        """修改个人信息"""
        parser = RequestParser()
        parser.add_argument('name', required=True, location='json', type=username_type)
        parser.add_argument('intro', required=True, location='json', type=str)
        # parser.add_argument('email', required=True, location='json', type=email_type)
        parser.add_argument('email', required=True, location='json')
        parser.add_argument('gender', required=True, location='json', type=str)
        parser.add_argument('age', required=True, location='json', type=int)

        # 获取参数
        args = parser.parse_args()
        name = args.name
        intro = args.intro
        email = args.email
        gender = args.gender
        age = args.age
        user_profile = UserProfile.query.options(load_only(UserProfile.user_id)).\
            filter(UserProfile.user_id==g.user_id).first()
        user_profile.user_basic.name = name
        user_profile.user_basic.introduction = intro
        user_profile.email = email
        user_profile.gender = gender
        user_profile.age = age

        db.session.commit()



        return user_profile.to_dict()






"""

# 上传头像
/user/photo
# 请求方式  
PATCH   form-data
# 请求参数  
photo   上传的头像文件

# 响应数据  json
{
  "photo_url": "www.xx.com/123.jpg"
}

"""


class UserPhotoResource(Resource):
    method_decorators = [login_required]
    def patch(self):
        """修改头像"""
        # 获取参数
        userid = g.user_id
        parser = RequestParser()
        parser.add_argument('photo', required=True, type=image_file, location='files')
        args = parser.parse_args()
        img_file = args.photo

        # 读取二进制数据
        img_bytes = img_file.read()
        try:
            file_url = upload_file(img_bytes)
        except BaseException as e:
            return {'message': 'thired Error: %s' %e, 'data': None}, 500

        # 将数据库中头像url进行更新
        User.query.filter(User.id == userid).update({'profile_photo': file_url})
        db.session.commit()

        # 将数据对象删除
        usercache = UserCache(userid)
        usercache.clear()

        return {'photo_url': file_url}



