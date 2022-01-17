from sqlalchemy.orm import load_only

from app import create_app, db
from flask import jsonify


# 创建web应用
from models.user import User

from common.models.user import Area, Article

app = create_app('dev')


@app.route('/')
def route_map():
    """定义根路由：获取所有路由规则"""
    area = Area.query.options(load_only(Area.id)).filter(Area.id== 788931).first()
    print(area.parent)
    # print(user.name,user.id)
    # art = db.session. \
    #     query(Area.area_name, Article.id,).join(Area, Article.area_id == Area.id).\
    #     filter(Article.id == 4).first()
    #
    # print(art)

    return jsonify({rule.endpoint: rule.rule for rule in app.url_map.iter_rules()})

