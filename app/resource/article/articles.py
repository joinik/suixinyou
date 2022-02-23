from datetime import datetime

from flask import g
from flask_restful import Resource
from flask_restful.reqparse import RequestParser
from sqlalchemy.orm import load_only

from app import db
from app.models.article import Article, ArticleContent, Category
from app.models.comment import LikeComment, DisLikeComment
from utils.constants import HOME_PRE_PAGE

from utils.decorators import login_required


class CategoryResource(Resource):
    """分类主类"""

    def get(self):
        # 数据库查询获取所有分类
        cat_list = Category.query.options(load_only(Category.id)).filter(Category.is_deleted == 0).all()

        # 组装分类结构
        cat_rest = [{"id": item.id, "name": item.cate_name} for item in cat_list]

        # 返回响应
        return {"message": "OK", "data": cat_rest}


class CategoryDetailResource(Resource):
    """获取分类下的所有文章"""

    def get(self):
        # 根据分类id 查询分类的所有文章
        parser = RequestParser()
        parser.add_argument("cate_id", required=True, location='args', type=int)
        parser.add_argument("timestamp", required=True, location='args', type=int)
        args = parser.parse_args()

        # 获取参数
        cate_id = args.cate_id
        timestamp = args.timestamp

        # 转换时间戳
        date = datetime.fromtimestamp(timestamp * 0.001)

        if timestamp == 0:
            rest = Article.query.filter(Article.category_id == cate_id, Article.status == Article.STATUS.APPROVED,
                                        ).order_by(
                Article.ctime.desc()).limit(HOME_PRE_PAGE).all()

        else:
            # 查询数据
            rest = db.session.query(Article.id, Article.title, Article.user_id, Article.ctime, Article.user,
                                    Article.area,
                                    Article.comment_count, Article.like_count, Article.dislike_count,
                                    ).filter(Article.category_id == cate_id, Article.status == Article.STATUS.APPROVED,
                                             Article.ctime < date).order_by(
                Article.ctime.desc()).limit(HOME_PRE_PAGE).all()

        print("分类结果", rest)
        data = [
            {"art_id": item.id,
             "title": item.title,
             "aut_id": item.user_id,
             "aut_name": item.user.name,
             "pubdate": item.ctime.isoformat(),
             "comment_count": item.comment_count,
             "like_count": item.like_count,
             "dislike_count": item.dislike_count,
             "area_id": item.area_id,
             "area_name": item.area.area_name
             }
            for item in rest
        ]

        pre_timestamp = int(rest[-1].ctime.timestamp() * 1000) if data else 0
        # 返回数据
        return {'results': data, 'pre_timestamp': pre_timestamp}


"""
获取游记信息

请求方式
GET

响应数据  json  200
{
    "message": "OK",
    "data": {
        "area_name": "北京市",
        "art_id": 3,
        "title": "江西井冈山之旅1",
        "pubdate": "2022-01-19T10:26:01",
        "update": "2022-01-19T10:41:49",
        "aut_id": 1,
        "aut_name": "dsf12123",
        "aut_photo": null,
        "content": "17年4月5日，我们一行十人（其中6人为高中同学），乘坐K495次列车，开始了江西宜春温汤之旅。这次旅行我们已期待很久，早在四个月前，就作了准备，在徐立华同学精心策划下，预订酒店，考虑旅行线路，今天终于出发了！经过一夜行程，于6日一早到达宜春火车站。徐导为我们预订的车辆已在门口等候，一行人浩浩荡荡来到泰轩温泉酒店。下图为酒店外观，及从住宿客房里看到的酒店温泉，还有远处眺望看到的温汤镇的景视。第一印象还不错",
        "comment_count": 0,
        "like_count": 0,
        "dislike_count": 0
    }
}

错误响应 403
{
    "message": "Access Violation",
    "data": null
}


"""


class ArticleDetailResource(Resource):
    method_decorators = {'put': [login_required]}

    def get(self, article_id):
        """查询文章"""
        print("文章id", article_id)
        # 查询基础数据

        data = Article.query.options(load_only(Article.id)). \
            filter(Article.id == article_id, Article.status == Article.STATUS.APPROVED).first()
        # print(data)
        # input("等待")
        if not data:
            return {'message': "Access Violation", 'data': None}, 403

        # 序列化
        article_dict = {
            'area_id': data.area.id,
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
        """修改文章"""
        parser = RequestParser()
        parser.add_argument('title', required=True, location='json', type=str)
        # parser.add_argument('cover', required=True, location='json', type=str)
        parser.add_argument('content', required=True, location='json', type=str)

        args = parser.parse_args()
        title = args.title
        content = args.content

        # 根据文章id，作者id是否是用户id 查询数据
        data = Article.query.options(load_only(Article.id)). \
            filter(Article.id == article_id, Article.status == 2, Article.user_id == g.user_id).first()

        if not data:
            return {'message': "Access Violation", 'data': None}, 403

        data.title = title
        data.content = content

        db.session.add(data)
        db.session.commit()

        return {'article': data.id, 'title': data.title, "uptime": data.utime.isoformat()}, 201


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

        try:
            # 存入数据库
            article = Article(category_id=category_id, user_id=user_id, area_id=area_id, title=title)
            print('存储文章基本信息')
            db.session.add(article)
            # 先执行插入插入操作， 才能获取article 的id
            db.session.flush()

            article.user.travel_note_num += 1

            print('存储文章内容')

            art_content = ArticleContent(article_id=article.id, content=content)
            db.session.add(art_content, article)
            db.session.commit()
            return {'article': article.id, 'title': article.title, 'time': article.ctime.isoformat()}, 201

        except Exception as e:
            db.session.rollback()
            print(e)
            return {'message': "Access Violation", 'data': None}, 403


"""
点赞API
前端 
用户 对 游记，用户，评论，点赞，发送请求
post  '/app/dolike/' 


后端
接收请求， 
返回json响应

"""


class LikeArticleResource(Resource):
    """点赞游记主类"""
    method_decorators = [login_required]

    def post(self):
        parser = RequestParser()
        parser.add_argument('art_id', required=True, location='json', type=int)
        args = parser.parse_args()
        art_id = args.art_id

        try:
            # 进行 游记点赞查询，
            # 查询到，则修改为取消点赞， 反之添加点赞

            like_model = LikeComment.query.options(load_only(LikeComment.liker_id)). \
                filter(LikeComment.liker_id == g.user_id, LikeComment.article_id == art_id).first()
            if not like_model:
                like_model = LikeComment(liker_id=g.user_id, article_id=art_id)
                db.session.add(like_model)
                db.session.flush()
                like_model.article.like_count += 1
            else:
                # 根据数据库记录的 判断是点赞还是取消
                if like_model.relation == 0:
                    like_model.relation = 1
                    like_model.article.like_count += 1

                else:
                    like_model.relation = 0
                    like_model.article.like_count -= 1

            db.session.add(like_model)
            db.session.commit()
            return {'liker_id': g.user_id, 'art_id': art_id, 'time': like_model.utime.isoformat()}, 201

        except Exception as e:
            print("点赞游记操作失败， ")
            print(e)
            db.session.rollback()
            return {"message": '操作失败！', 'data': None}, 400


class LikeUserResource(Resource):
    """点赞用户主类"""
    method_decorators = [login_required]

    def post(self):
        parser = RequestParser()
        parser.add_argument('user_id', required=True, location='json', type=int)

        args = parser.parse_args()
        user_id = args.user_id

        try:
            # 进行 用户点赞查询，
            # 查询到，则修改为取消点赞， 反之添加点赞

            like_model = LikeComment.query.options(load_only(LikeComment.liker_id)). \
                filter(LikeComment.liker_id == g.user_id, LikeComment.liked_id == user_id).first()
            if not like_model:
                like_model = LikeComment(liker_id=g.user_id, liked_id=user_id)
                db.session.add(like_model)
                db.session.flush()
                like_model.liked.dianzan_num += 1

            else:
                # 判断是点赞还是取消
                if like_model.relation == 0:
                    like_model.relation = 1
                    like_model.liked.dianzan_num += 1
                else:
                    like_model.relation = 0
                    like_model.liked.dianzan_num -= 1

            db.session.add(like_model)
            db.session.commit()
            return {'liker_id': g.user_id, 'liked_id': user_id, 'time': like_model.utime.isoformat()}, 201

        except Exception as e:
            print("点赞用户操作失败， ")
            print(e)
            db.session.rollback()
            return {"message": '操作失败！', 'data': None}, 400


class LikeCommentResource(Resource):
    """点赞评论主类"""
    method_decorators = [login_required]

    def post(self):
        parser = RequestParser()
        parser.add_argument('comment_id', required=True, location='json', type=int)

        args = parser.parse_args()
        comment_id = args.comment_id

        try:
            # 进行 评论点赞查询，
            # 查询到，则修改为取消点赞， 反之添加点赞

            like_model = LikeComment.query.options(load_only(LikeComment.liker_id)). \
                filter(LikeComment.liker_id == g.user_id, LikeComment.comment_id == comment_id).first()
            if not like_model:
                like_model = LikeComment(liker_id=g.user_id, comment_id=comment_id)

                db.session.add(like_model)
                db.session.flush()

                like_model.comment.like_count += 1

            else:
                # 判断是点赞还是取消
                if like_model.relation == 0:
                    like_model.relation = 1
                    like_model.comment.like_count += 1
                else:
                    like_model.relation = 0
                    like_model.comment.like_count -= 1

            db.session.add(like_model)
            db.session.commit()

            return {'liker_id': g.user_id, 'comment_id': comment_id, 'time': like_model.utime.isoformat()}, 201

        except Exception as e:
            print("点赞评论操作失败， ")
            print(e)
            db.session.rollback()
            return {"message": '操作失败！', 'data': None}, 400


class DisLikeArticleResource(Resource):
    """点踩游记 or 评论 主类"""
    method_decorators = [login_required]

    def post(self):
        parser = RequestParser()
        parser.add_argument('art_id', location='json', type=int)
        parser.add_argument('comment_id', location='json', type=int)
        args = parser.parse_args()
        art_id = args.art_id
        comment_id = args.comment_id

        if (not art_id) and (not comment_id):
            return {"message": 'Invalid Access！', 'data': None}, 400

        if art_id:
            try:
                # 进行 游记点踩查询，
                # 查询到，则修改为取消点踩， 反之添加点踩

                like_model = DisLikeComment.query.options(load_only(DisLikeComment.id)). \
                    filter(DisLikeComment.disliker_id == g.user_id, DisLikeComment.article_id == art_id).first()
                if not like_model:
                    like_model = DisLikeComment(disliker_id=g.user_id, article_id=art_id)
                    db.session.add(like_model)
                    db.session.flush()
                    like_model.article.dislike_count += 1
                else:
                    # 根据数据库记录的 判断是点赞还是取消
                    if like_model.relation == 0:
                        like_model.relation = 1
                        like_model.article.dislike_count += 1

                    else:
                        like_model.relation = 0
                        like_model.article.dislike_count -= 1

                db.session.add(like_model)
                db.session.commit()
                return {'disliker_id': g.user_id, 'art_id': art_id, 'time': like_model.utime.isoformat()}, 201

            except Exception as e:
                print("点踩游记操作失败， ")
                print(e)
                db.session.rollback()
                return {"message": '操作失败！', 'data': None}, 400

        elif comment_id:
            try:
                # 进行 评论点踩查询，
                # 查询到，则修改为取消点踩， 反之添加点踩

                like_model = DisLikeComment.query.options(load_only(DisLikeComment.id)). \
                    filter(DisLikeComment.disliker_id == g.user_id, DisLikeComment.comment_id == comment_id).first()
                if not like_model:
                    like_model = DisLikeComment(disliker_id=g.user_id, comment_id=comment_id)
                    db.session.add(like_model)
                    db.session.flush()
                    like_model.article.dislike_count += 1
                else:
                    # 根据数据库记录的 判断是点赞还是取消
                    if like_model.relation == 0:
                        like_model.relation = 1
                        like_model.article.dislike_count += 1

                    else:
                        like_model.relation = 0
                        like_model.article.dislike_count -= 1

                db.session.add(like_model)
                db.session.commit()
                return {'disliker_id': g.user_id, 'comment_id': comment_id, 'time': like_model.utime.isoformat()}, 201

            except Exception as e:
                print("点踩游记操作失败， ")
                print(e)
                db.session.rollback()
                return {"message": '操作失败！', 'data': None}, 400





