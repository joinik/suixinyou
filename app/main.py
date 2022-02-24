import asyncio
import json

from sqlalchemy.orm import load_only

from app import create_app, db
from flask import jsonify, request
import httpx

# 创建web应用
from app.models.area import Area
from app.models.article import Category
from common.utils.req_weather import async_weather

app = create_app('dev')


@app.route('/app/ip', methods=["POST"])
def user_ip():
    area_id = request.json.get("area_id")
    area_name = request.json.get("area_name")

    # 根据前端发送的 用户地址信息
    try:
        # 1. 数据库查询 用户城市的文章信息
        area_model = Area.query.options(load_only(Area.id)).filter(Area.area_name.like('%' + area_name + '%')).first()
    except Exception as e:
        print("地区查询 数据库，失败", )
        print(e)
        return {"message": "Invalid Access", "data": None}, 401

    # 1.1 数据序列化
    area_article = [item.todict() for item in area_model.articles]

    # print("文章数据")
    # print(area_article)

    # 2. 进行天气查询
    html = async_weather(area_model.area_name)

    return jsonify({"message": "OK", "data": {"area_article": area_article, "weather": html}})


@app.route('/')
def route_map():
    """定义根路由：获取所有路由规则"""

    # user = LikeComment.query.options(load_only(LikeComment.id)).filter(LikeComment.id ==3).first()
    # print(user.article.like_count)
    cat = Category(cate_name="神秘")
    db.session.add(cat)
    db.session.commit()
    return jsonify({rule.endpoint: rule.rule for rule in app.url_map.iter_rules()})
