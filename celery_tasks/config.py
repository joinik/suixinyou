from celery.schedules import crontab

from app import redis_master

broker_url = "redis://192.168.17.131:6381/15"

###########################说明#############################

# 如果使用别的作为中间人, 例如使用 rabbitmq
# 则 rabbitmq 配置如下:
# broker_url= 'amqp://用户名:密码@ip地址:5672'

# 例如:
# meihao: 在rabbitq中创建的用户名, 注意: 远端链接时不能使用guest账户.
# 123456: 在rabbitq中用户名对应的密码
# ip部分: 指的是当前rabbitq所在的电脑ip
# 5672: 是规定的端口号
# broker_url = 'amqp://meihao:123456@172.16.238.128:5672'


# 设置时区
timezone = 'Asia/Shanghai'
enable_utc = True


# 声明定时任务
# beat_schedule = {
#     'add_6hours_req_weather': {		# 任务名，可以自定义
#         "task": "celery_tasks.weather.tasks.celery_request_weather",	# 任务函数
#         "schedule": crontab(minute=0, hour=6),	# 定时每30秒执行一次(从开启任务时间计算)
#         "args": (),		# 传未定义的不定长参数
#         # 'kwargs': ({'name':'张三'}),	# 传已定义的不定长参数
#     }
#     # u'inputsysapp_tasks_delete': {
#     #     "task": "inputsysapp.tasks.delete",
#     #     "schedule": crontab(minute='*/1'),		# 定时每1分钟执行一次(每分钟的0秒开始执行)
#     #     # "args": (),
#     #     # 'kwargs': (),
#     # },
# }
