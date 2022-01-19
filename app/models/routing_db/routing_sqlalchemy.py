import random
from flask_sqlalchemy import SQLAlchemy, SignallingSession, get_state
from sqlalchemy import orm


# 设置多个数据库的URI (用于数据操作)
# app.config['SQLALCHEMY_BINDS'] = {
#     'master': 'mysql://root:mysql@10.211.55.14:3306/test31',
#     'slave1': 'mysql://root:mysql@10.211.55.14:8306/test31',
#     'slave2': 'mysql://root:mysql@10.211.55.14:8306/test31'
# }


class RoutingSession(SignallingSession):
    """自定义Session类, 继承SignallingSession"""

    def __init__(self, *args, **kwargs):
        super(RoutingSession, self).__init__(*args, **kwargs)
        # 每个Session(请求), 随机一次从库, 避免每个请求访问多个从库影响性能
        self.slave = random.choice(['slave1', 'slave2'])

    def get_bind(self, mapper=None, clause=None):
        """每次数据库操作(增删改查及事务操作)都会调用该方法, 来获取对应的数据库引擎(访问的数据库)"""

        state = get_state(self.app)
        if self._bind:   # 判断该查询是否指定的了访问的数据库, 如果有指定, 则使用该数据库
            return state.db.get_engine(self.app, bind=self._bind)

        elif mapper is not None:  # 如果该操作中涉及的模型类和数据表建立了映射
            try:
                # SA >= 1.3
                persist_selectable = mapper.persist_selectable
            except AttributeError:
                # SA < 1.3
                persist_selectable = mapper.mapped_table

            info = getattr(persist_selectable, 'info', {})
            bind_key = info.get('bind_key')  # 查询模型类是否指定了访问的数据库

            if bind_key is not None:  # 如果该模型类已指定数据库, 使用指定的数据库
                return state.db.get_engine(self.app, bind=bind_key)

        if self._flushing:  # 如果模型类未指定数据库, 判断是否为写操作
            print('写操作')
            return state.db.get_engine(self.app, bind='master')
        else:

            print('读操作: ', self.slave)
            return state.db.get_engine(self.app, bind=self.slave)

    _bind = None  # 给属性设置默认值, 防止报错

    def using_bind(self, bind):
        """
        指定要访问的数据库
        :param bind: 数据库的别名
        :return: session对象
        """
        self._bind = bind
        return self


class RoutingSQLAlchemy(SQLAlchemy):
    """自定义SQLALchemy类"""

    def create_session(self, options):
        """重写create_session方法: 使用自定义Session类"""
        return orm.sessionmaker(class_=RoutingSession, db=self, **options)


