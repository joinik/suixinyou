from flask import g
from flask_restful import Resource
from flask_restful.reqparse import RequestParser
from sqlalchemy.orm import load_only

from app import db
from app.models.user import Article, ArticleContent, User, Area

from common.utils.decorators import login_required


class ArticleDetailResource(Resource):
    method_decorators = {'put': [login_required]}
    def get(self, article_id):
        print("文章id",article_id)
        # 查询基础数据

        data = Article.query.options(load_only(Article.id)).\
            filter(Article.id == article_id, Article.status == 2).first()
        # print(data)
        # input("等待")
        if not data:
            return {'message': "Access Violation", 'data': None}, 403


        # 序列化
        article_dict = {
            'area_name': data.area.area_name,
            'art_id': data.id,
            'title': data.title,
            'pubdate': data.ctime.isoformat(),
            'update': data.utime.isoformat(),
            'aut_id': data.user.id,
            'aut_name': data.user.name,
            'aut_photo': data.user.profile_photo,
            'content': data.article_content.content,
            'comment_count': data.comment_count,
            'like_count': data.like_count,
            'dislike_count': data.dislike_count
        }

        # 返回数据
        return article_dict

    def put(self, article_id):
        parser = RequestParser()
        parser.add_argument('title', required=True, location='json', type=str)
        # parser.add_argument('cover', required=True, location='json', type=str)
        parser.add_argument('content', required=True, location='json', type=str)

        args = parser.parse_args()
        title = args.title
        content = args.content

        data = Article.query.options(load_only(Article.id)). \
            filter(Article.id == article_id, Article.status == 2).first()

        if not data:
            return {'message': "Access Violation", 'data': None}, 403


        data.title = title
        data.content = content

        db.session.add(data)
        db.session.commit()

        return {'article': data.id, 'title': data.title}, 201


class CreateArticleResource(Resource):
    method_decorators = {'post': [login_required]}

    def post(self):
        """创建文章"""
        parser = RequestParser()
        parser.add_argument('category_id', required=True, location='json', type=int)
        parser.add_argument('area_id', required=True, location='json', type=int)
        parser.add_argument('title', required=True, location='json', type=str)
        # parser.add_argument('cover', required=True, location='json', type=str)
        parser.add_argument('content', required=True, location='json', type=str)

        args = parser.parse_args()
        user_id = g.user_id

        category_id = args.category_id
        area_id = args.area_id
        title = args.title
        content = args.content



        # 存入数据库

        article = Article(category_id=category_id, user_id=user_id, area_id=area_id, title=title)
        print('存储文章基本信息')
        db.session.add(article)
        # 先执行插入插入操作， 才能获取article 的id
        db.session.flush()
        # db.session.commit()
        print('存储文章内容')
        # article_id = db.session.query(Article).order_by(Article.ctime.desc()).all()[0]
        art_content = ArticleContent(article_id=article.id, content=content)
        db.session.add(art_content)
        db.session.commit()

        return {'article': article.id, 'title': article.title}, 201


# class CreateArticleResource(Resource):
