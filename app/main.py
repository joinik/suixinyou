from sqlalchemy.orm import load_only

from app import create_app, db
from flask import jsonify, request

# 创建web应用
from .models.user import User, Article, Area, LikeComment, Comment

app = create_app('dev')


@app.route('/')
def route_map():
    """定义根路由：获取所有路由规则"""

    user = LikeComment.query.options(load_only(LikeComment.id)).filter(LikeComment.id ==3).first()
    print(user.article.like_count)
    # user_ip = request.remote_addr
    # print(user_ip)
    return jsonify({rule.endpoint: rule.rule for rule in app.url_map.iter_rules()})

