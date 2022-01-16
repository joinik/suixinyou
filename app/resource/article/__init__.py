


from .articles import  ArticleDetailResource

# 添加类视图
article_api.add_resource(ArticleDetailResource, '/articles/<int:article_id>')