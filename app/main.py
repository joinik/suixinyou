from sqlalchemy.orm import load_only

from app import create_app
from flask import jsonify


# 创建web应用
from models.user import User

app = create_app('dev')


@app.route('/')
def route_map():
    """定义根路由：获取所有路由规则"""
    user = User.query.options(load_only(User.id)).filter(User.id== 1).first()
    print(user.name,user.id)

    return jsonify({rule.endpoint: rule.rule for rule in app.url_map.iter_rules()})

