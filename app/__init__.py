# -*- coding: utf-8 -*-
# author: JK time:2021/12/22


from flask import Flask
from os.path import *
import sys


# 将common路径加入模块查询路径
BASE_DIR = dirname(dirname(abspath(__file__)))
sys.path.insert(0, BASE_DIR + '/common')
sys.path.insert(1, BASE_DIR + '/celery_tasks')


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


from celery import Celery



#使celery接入Flask上下文
def register_celery(app=None):
    celery.config_from_object('celery_tasks.config')

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery







from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis

# sqlalchemy 组件对象
db = SQLAlchemy()

# redis数据库操作对象
redis_client = None     # type: StrictRedis

def register_extensions(app):
    """组件初始化"""

    # sqlalchemy组件初始化
    from app import db
    db.init_app(app)

    # redis组件初始化
    global redis_client
    redis_client = StrictRedis(host=app.config['REDIS_HOST'], port=app.config['REDIS_PORT'], decode_responses=True)

    # 添加转换器
    from utils.converters import register_converters
    register_converters(app)


def register_bp(app:Flask):
    """注册蓝图"""
    from app.resource.user import user_bp # 进行局部导入，避免组件没有初始化完成
    app.register_blueprint(user_bp)



def create_app(type):
    """创建应用 和组件初始化"""
    app = create_flask_app(type)

    # 组件初始化
    # register_celery(app=app)
    register_extensions(app)
    # app.app_context().push()
    # 注册蓝图
    register_bp(app)


    return app

