

class DefaultConfig():
    """默认配置"""
    # 数据库mysql配置
    SQLALCHEMY_DATABASE_URL = 'mysql://suixin:mysql@192.168.17.128:3306/suixinyou'
    SQLALCHEMY_TRACK_MODIFICATIONS = False # 是否追踪数据变化
    SQLALCHEMY_ECHO = False # 是否打印底层执行的sql

    # redis配置
    REDIS_HOST = '192.168.17.128'   # ip
    REDIS_PORT = 6381  # 端口

config_dict = {
    'dev': DefaultConfig
}