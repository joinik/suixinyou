
from flask import Blueprint
from flask_restful import Api
from .passport import SMSCodeResource, MobileResource, LoginResource
from utils.constants import BASE_URL_PRIFIX

# 1.创建蓝图对象
from .profile import CurrentUserResource, UserPhotoResource, UserInfoResource
from .router_card import TravelCardResource, WeatherResource

user_bp = Blueprint('user', __name__, url_prefix=BASE_URL_PRIFIX)

# 2.创建Api对象
user_api = Api(user_bp)



# 设置json包装格式
from utils.output import output_json
user_api.representation('application/json')(output_json)

# 3.添加类视图
user_api.add_resource(SMSCodeResource, '/sms/codes/<mob:mobile>')
# user_api.add_resource(UsernameResource, '/usernames/<uname:username>')
# 手机号方式登录
user_api.add_resource(LoginResource, '/authorizations')
# 微信登录
# user_api.add_resource(LoginResource, '/authorizations')

# 个人信息
user_api.add_resource(CurrentUserResource, '/user')
user_api.add_resource(UserInfoResource, '/user/info')
user_api.add_resource(UserPhotoResource, '/user/photo')
user_api.add_resource(TravelCardResource, '/travel_card')
user_api.add_resource(WeatherResource, '/ip')


