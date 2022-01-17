

from flask import Flask
from os.path import *
import sys


# 将common路径加入模块查询路径
from flask_migrate import Migrate
from redis.sentinel import Sentinel
from rediscluster import RedisCluster

BASE_DIR = dirname(dirname(abspath(__file__)))
sys.path.insert(0, BASE_DIR + '/common')
sys.path.insert(1, BASE_DIR + '/celery_tasks')
sys.path.insert(2, BASE_DIR + '/common/models')


from app.settings.config import config_dict
from utils.constants import EXTRA_ENV_CONFIG

def create_flask_app(type):
    """创建flask应用"""

    # 创建flask应用
    app = Flask(__name__)
    # 根据类型加载配置子类
    config_class = config_dict[type]

    # 先加载默认配置
    app.config.from_object(config_class)

    # 在加载额外配置
    app.config.from_envvar(EXTRA_ENV_CONFIG, silent=True)

    # 返回应用
    return app


from redis import StrictRedis

from flask_sqlalchemy import SQLAlchemy
# # sqlalchemy 组件对象
db = SQLAlchemy()

from models.routing_db.routing_sqlalchemy import RoutingSQLAlchemy

# mysql数据库操作对象
# db = RoutingSQLAlchemy()


redis_master = None  # type: StrictRedis
redis_slave = None  # type: StrictRed

# 创建集群客户端对象
redis_cluster = None



def register_extensions(app):
    """组件初始化"""

    # sqlalchemy组件初始化
    from app import db
    db.init_app(app)

    # redis组件初始化
    # global redis_client
    # redis_client = StrictRedis(host=app.config['REDIS_HOST'], port=app.config['REDIS_PORT'], decode_responses=True)


    # redis集群组件初始化
    global redis_cluster
    redis_cluster = RedisCluster(startup_nodes=app.config['CLUSTER_NODES'], decode_responses=True, )

    # 数据迁移组件初始化
    Migrate(app, db)
    # 导入模型类
    from models import user

    # 添加转换器
    from utils.converters import register_converters
    register_converters(app)

    # 添加请求钩子
    from utils.middlewares import get_userinfo
    app.before_request(get_userinfo)


def register_bp(app:Flask):
    """注册蓝图"""
    from app.resource.user import user_bp # 进行局部导入，避免组件没有初始化完成
    from app.resource.article import article_bp
    app.register_blueprint(user_bp)
    app.register_blueprint(article_bp)



def create_app(type):
    """创建应用 和组件初始化"""
    app = create_flask_app(type)

    # 组件初始化
    register_extensions(app)

    # 注册蓝图
    register_bp(app)

    return app

