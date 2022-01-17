from flask import Blueprint
from flask_restful import Api

from utils.constants import BASE_URL_PRIFIX
from .articles import ArticleDetailResource, CreateArticleResource

article_bp = Blueprint('articles', __name__, url_prefix=BASE_URL_PRIFIX)

# 2.创建Api对象
article_api = Api(article_bp)




# 添加类视图
article_api.add_resource(ArticleDetailResource, '/articles/<int:article_id>')
article_api.add_resource(CreateArticleResource, '/articles/create')
