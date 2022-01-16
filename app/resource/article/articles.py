# # app/resources/article/articles.py
# from app import db
# from common.models.article import Article
#
# ...
#
# from models.article import ArticleContent
#
# ...
#
#
# class ArticleDetailResource(Resource):
#     def get(self, article_id):
#         # 查询基础数据
#         data = db.session.\
#             query(Article.id, Article.title, Article.ctime, Article.user_id, User.name, User.profile_photo, ArticleContent.content).\
#             join(User, Article.user_id == User.id).\
#             join(ArticleContent, Article.id == ArticleContent.article_id).\
#             filter(Article.id == article_id).first()
#
#         # 序列化
#         article_dict = {
#             'art_id': data.id,
#             'title': data.title,
#             'pubdate': data.ctime.isoformat(),
#             'aut_id': data.user_id,
#             'aut_name': data.name,
#             'aut_photo': data.profile_photo,
#             'content': data.content,
#             'is_followed': False,
#             'attitude': -1,
#             'is_collected': False
#         }
#
#         # 返回数据
#         return article_dict