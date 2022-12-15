

class DefaultConfig:
    """默认配置"""
    # 数据库mysql配置
    SQLALCHEMY_DATABASE_URI = "mysql://root:mysql@192.168.17.131:3306/suixinyou1"
    SQLALCHEMY_TRACK_MODIFICATIONS = False # 是否追踪数据变化
    SQLALCHEMY_ECHO = False # 是否打印底层执行的sql

    # SQLALCHEMY_BINDS = {  # 主从数据库的URI
    #     "master": 'mysql://root:mysql@192.168.17.128:3306/suixinyou',
    #     "slave1": 'mysql://root:mysql@192.168.17.128:3306/suixinyou',
    #     "slave2": 'mysql://root:mysql@192.168.17.128:8306/suixinyou'
    # }

    # # 设置哨兵的ip和端口
    # SENTINEL_LIST = [
    #     ('192.168.17.131', 26380),
    #     ('192.168.17.131', 26381),
    #     ('192.168.17.131', 26382),
    # ]

    # SERVICE_NAME = 'mymaster'  # 哨兵配置的主数据库别名

    # redis集群配置
    CLUSTER_NODES = [  # 集群中主数据库的ip和端口号
        {'host': '192.168.17.131', 'port': 7001},
        {'host': '192.168.17.131', 'port': 7002},
        {'host': '192.168.17.131', 'port': 7003},
        {'host': '192.168.17.131', 'port': 7004},
        {'host': '192.168.17.131', 'port': 7005},
        {'host': '192.168.17.131', 'port': 7000},
    ]

    #
    # elasticsearch集群服务器的地址
    ES = [
        '192.168.17.131:9200'
    ]

    # JWT
    JWT_SECRET = 'TPmi4aLWRbyVq8zu9v81dWYW17/z+UvRnYTt4P6fAXA'  # 秘钥
    JWT_EXPIRE_DAYS = 14  # JWT过期时间
    JWT_EXPIRE_HOURS = 2  # token 过期时间

    # 七牛云
    QINIU_ACCESS_KEY = ''
    QINIU_SECRET_KEY = ''
    QINIU_BUCKET_NAME = 'suixinyou1'
    QINIU_DOMAIN = 'http://r7r21o73n.hn-bkt.clouddn.com/'


config_dict = {
    'dev': DefaultConfig
}