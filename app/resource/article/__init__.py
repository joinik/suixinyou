from flask import Blueprint
from flask_restful import Api

from utils.constants import BASE_URL_PRIFIX
from .articles import ArticleDetailResource, CreateArticleResource, \
    LikeArticleResource, LikeUserResource, LikeCommentResource, DisLikeArticleResource, CategoryResource, \
    CategoryDetailResource, SpecialResource, ArticlePhoto

article_bp = Blueprint('articles', __name__, url_prefix=BASE_URL_PRIFIX)

# 2.创建Api对象
article_api = Api(article_bp)

# 设置json包装格式
from utils.output import output_json

article_api.representation('application/json')(output_json)

# 添加类视图
# 获取分类
article_api.add_resource(CategoryResource, '/Category')
article_api.add_resource(CategoryDetailResource, '/CategoryDetail')
article_api.add_resource(ArticlePhoto, '/UploadPhoto')
article_api.add_resource(ArticleDetailResource, '/articles/<int:article_id>')
article_api.add_resource(CreateArticleResource, '/articles/create')
article_api.add_resource(LikeArticleResource, '/articles/likes')
article_api.add_resource(LikeUserResource, '/users/likes')
article_api.add_resource(LikeCommentResource, '/comment/likes')
article_api.add_resource(DisLikeArticleResource, '/articles/dislikes')
article_api.add_resource(SpecialResource, '/special')



