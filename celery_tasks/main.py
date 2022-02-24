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


#