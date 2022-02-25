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


@app.route('/app/ip', methods=["GET"])
def user_ip():
    ip = request.remote_addr

    #  通过ip 获取 地理位置
    resp = httpx.get('https://restapi.amap.com/v5/ip?key=677f025efeda715a72a7837f85f576f9&type=4&ip={}'.format(ip))

    resp = resp.json()
    city = resp.get('city', '宿迁市')


    # 根据前端发送的 用户地址信息
    try:
        # 1. 数据库查询 用户城市的文章信息
        area_model = Area.query.options(load_only(Area.id)).filter(Area.area_name.like('%' + city + '%')).first()
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

    # 首页展示

    cat_model = Category.query.options(load_only(Category.id)).filter(Category.is_deleted == 0).all()


    rest = []
    for item in cat_model:

        art = [ item.todict()  for item in item.articles.limit(5).all()]
        rest.append({item.cate_name: art})
    # input('等待')



    return jsonify({"message": "OK", "data":rest})
