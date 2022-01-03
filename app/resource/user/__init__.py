
from flask import Blueprint
from flask_restful import Api
from .passport import SMSCodeResource, RegisterResource, LoginResource, UsernameResource, MobileResource
from utils.constants import BASE_URL_PRIFIX

# 1.创建蓝图对象
user_bp = Blueprint('user', __name__, url_prefix=BASE_URL_PRIFIX)

# 2.创建Api对象
user_api = Api(user_bp)



# 设置json包装格式
from utils.output import output_json
user_api.representation('application/json')(output_json)

# 3.添加类视图
user_api.add_resource(SMSCodeResource, '/sms/codes/<mob:mobile>')
user_api.add_resource(UsernameResource, '/usernames/<uname:username>')
user_api.add_resource(MobileResource, '/mobiles/<mob:mobile>')
user_api.add_resource(RegisterResource, '/register')
user_api.add_resource(LoginResource, '/login')

