# celery启动文件
import os
from datetime import timedelta

from celery import Celery



# 创建celery实例
from celery.schedules import crontab

celery_app = Celery('suixinyouTravel')

# 设置
celery_app.config_from_object("celery_tasks.config")

# 自动检测任务
celery_app.autodiscover_tasks(["celery_tasks.sms","celery_tasks.weather",])


#  定时任务
celery_app.conf.beat_schedule = {
    'add_6hours_req_weather': {		# 任务名，可以自定义
        "task": "celery_tasks.weather.tasks.celery_request_weather",	# 任务函数
        "schedule": crontab(minute='0', hour='6'),	# 定时每6小时执行一次(从开启任务时间计算)
        "args": (),		# 传未定义的不定长参数
        # 'kwargs': ({'name':'张三'}),	# 传已定义的不定长参数
    }
}