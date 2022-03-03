
from sqlalchemy.orm import load_only

from app import create_app
from flask import jsonify


# 创建web应用

from app.models.article import Category


app = create_app('dev')




@app.route('/')
def route_map():
    # 首页展示

    cat_model = Category.query.options(load_only(Category.id)).filter(Category.is_deleted == 0).all()

    rest = []
    for item in cat_model:
        art = [item.todict() for item in item.articles.limit(5).all()]
        rest.append({item.cate_name: art})
    # input('等待')

    return jsonify({"message": "OK", "data": rest})
