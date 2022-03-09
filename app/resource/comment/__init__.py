from flask import Blueprint
from flask_restful import Api

from utils.constants import BASE_URL_PRIFIX

from app.resource.comment.comment import CommentCreateResource

comment_bp = Blueprint('comment', __name__, url_prefix=BASE_URL_PRIFIX)

# 2.创建Api对象
comment_api = Api(comment_bp)

# 设置json包装格式
from utils.output import output_json

comment_api.representation('application/json')(output_json)

# 添加类视图
comment_api.add_resource(CommentCreateResource, '/comments')

# article_api.add_resource(CreateArticleResource, '/articles/create')
# article_api.add_resource(LikeArticleResource, '/articles/likes')
# article_api.add_resource(LikeUserResource, '/users/likes')
# article_api.add_resource(LikeCommentResource, '/comment/likes')
