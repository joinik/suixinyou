from flask import g
from flask_restful import Resource
from flask_restful.reqparse import RequestParser
from sqlalchemy.orm import load_only

from utils.decorators import login_required

from models.user import User

from utils.parser import image_file

from app import db
from common.utils.img_storage import upload_file

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


class CurrentUserResource(Resource):
    """个人中心-当前用户"""
    method_decorators = {'get': [login_required]}
    def get(self):
        userid = g.user_id

        # 查询用户数据
        user = User.query.options(load_only(User.id, User.name, User.profile_photo, User.introduction, User.dianzan_num, User.travel_note_num, User.dianliang_area_num))\
            .filter(User.id == userid).first()

        return user.to_dict()



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
        userid = g.userid
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

        return {'photo_url': file_url}



