from flask import g, request
from flask_restful import Resource
from flask_restful.reqparse import RequestParser
from sqlalchemy.orm import load_only

from utils.decorators import login_required

from app import db
from app.models.comment import Comment
from common.cache.weather import WeatherCache


class CommentCreateResource(Resource):
    method_decorators = {"post": [login_required]}

    def post(self):

        parser = RequestParser()
        parser.add_argument('art_id', required=True, location='json', type=int)
        parser.add_argument('parent_id', location='json', type=int)
        parser.add_argument('comment_text', required=True, location='json', type=str)
        args = parser.parse_args()

        # 获取参数

        art_id = args.art_id
        parent_id = args.parent_id
        comment_text = args.comment_text

        # 获取用户id
        user_id = g.user_id

        if parent_id:
            # 如果传递过来了父评论的id，那么则是对评论进行评论
            try:
                # 查询父评论
                parent_comment = Comment.query.options(load_only(Comment.comment_id)).\
                    filter(Comment.comment_id == parent_id, Comment.status ==1).first()
                parent_comment.reply_count += 1

            except Exception as e:
                db.session.rollback()
                print("父评论数据库查询失败", e)
                return {'message': "comment fail", 'data': None}, 403

            try:
                comment_model = Comment(article_id=art_id, user_id=user_id, parent_id=parent_id, content=comment_text)
                db.session.add(comment_model, parent_comment)
                db.session.flush()

                comment_model.article.comment_count +=1
                db.session.add(comment_model)
                db.session.commit()
                # 清除 redis中的文章 缓存
                wc = WeatherCache(areaid=comment_model.article.area_id)
                wc.clear()


                return {"art": art_id, "parent": parent_comment.comment_id, "comment_id": comment_model.comment_id, "time": comment_model.ctime.isoformat()}, 201

            except Exception as e:
                db.session.rollback()
                print("评论数据库创建失败", e)
                return {'message': "comment fail", 'data': None}, 403

        else:
            # 如果没有 则存储评论到数据库
            try:
                comment_model = Comment(article_id=art_id, user_id=user_id,
                                        content=comment_text)
                db.session.add(comment_model)
                db.session.flush()
                comment_model.article.comment_count += 1
                db.session.add(comment_model)
                db.session.commit()

                # 清除 redis中的文章 缓存
                wc = WeatherCache(areaid=comment_model.article.area_id)
                wc.clear()

                return {"art": art_id, "comment_id": comment_model.comment_id, "time": comment_model.ctime.isoformat()}, 201

            except Exception as e:
                db.session.rollback()
                print("评论数据库创建失败", e)
                return {'message': "comment fail", 'data': None}, 400

    def get(self):
        """查看评论"""
        # 构造请求参数
        parser = RequestParser()
        parser.add_argument('art_id', required=True, location='args', type=int)
        parser.add_argument('offset', default=0, location='args', type=int)
        parser.add_argument('limit', default=10, location='args', type=int)
        args = parser.parse_args()
        art_id = args.art_id
        offset = args.offset
        limit = args.limit

        # 进行数据库查询
        comments = Comment.query.options(load_only(Comment.comment_id)).\
            filter(Comment.article_id == art_id,Comment.comment_id > offset, Comment.status == Comment.STATUS.APPROVED).\
            limit(limit).all()

        comment_list = [{
            "com_id": item.comment_id,
            "aut_id": item.user.id,
            "aut_name": item.user.name,
            "aut_photo": item.user.profile_photo,
            "pubdate": item.ctime.isoformat(),
            "content": item.content,
            "reply_count": item.reply_count,
            "like_count": item.like_count
        } for item in comments]

        # 查询评论总数
        total_count = Comment.query.filter(Comment.article_id == art_id, Comment.status == Comment.STATUS.APPROVED).count()

        # 所有评论中最后一条评论的id
        end_comment = db.session.query(Comment.comment_id).filter(Comment.article_id == art_id, Comment.status == Comment.STATUS.APPROVED).order_by(
            Comment.comment_id.desc()).first()
        end_id = end_comment.comment_id if end_comment else None

        # 获取本次请求最后一条数据的id
        last_id = comments[-1].comment_id if comments else None

        # 返回数据
        return {'results': comment_list, 'total_count': total_count, 'last_id': last_id, 'end_id': end_id}

