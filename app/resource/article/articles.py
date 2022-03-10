import json
from datetime import datetime

from flask import g, request
from flask_restful import Resource
from flask_restful.reqparse import RequestParser
from sqlalchemy.orm import load_only

from app import db
from app.models.area import Area
from app.models.article import Article, ArticleContent, Category, Special
from app.models.comment import LikeComment, DisLikeComment
from utils.constants import HOME_PRE_PAGE

from utils.decorators import login_required

from app.models.user import User
from common.cache.users import UserCache
from common.cache.weather import WeatherCache
from common.utils.img_storage import upload_file
from common.utils.parser import image_file

"""分类主类"""


class CategoryResource(Resource):

    def get(self):
        # 数据库查询获取所有分类
        # print("分类查询")
        try:
            cat_list = Category.query.options(load_only(Category.id)).filter(Category.is_deleted == 0).all()
            # print(cat_list)
        except Exception as e:
            print('分类查询 失败')
            print(e)
            return {'message': "Access Violation", 'data': None}, 403

        # 组装分类结构
        cat_rest = [{"id": item.id, "name": item.cate_name} for item in cat_list]

        # 返回响应
        return cat_rest


class CategoryDetailResource(Resource):
    """获取分类下的所有文章"""

    def get(self):
        # 根据分类id 查询分类的所有文章
        parser = RequestParser()
        parser.add_argument("cate_id", required=True, location='args', type=int)
        parser.add_argument("timestamp", default=0, location='args', type=int)
        args = parser.parse_args()

        # 获取参数
        cate_id = args.cate_id
        timestamp = args.timestamp

        # 转换时间戳
        date = datetime.fromtimestamp(timestamp * 0.001)

        try:
            if timestamp == 0:
                rest = Article.query.filter(Article.category_id == cate_id, Article.status == Article.STATUS.APPROVED,
                                            ).order_by(
                    Article.ctime.desc()).limit(HOME_PRE_PAGE).all()

            else:
                # 查询数据
                rest = Article.query.filter(Article.category_id == cate_id,
                                              Article.status == Article.STATUS.APPROVED,
                                              Article.ctime < date).order_by(
                    Article.ctime.desc()).limit(HOME_PRE_PAGE).all()

        except Exception as e:
            print('查询分类下的文章')
            print(e)
            return {"message": "系统 升级中，稍后再试"}, 402

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
    method_decorators = {'put': [login_required], 'delete': [login_required]}

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
        article_dict = data.to_dict()

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
            filter(Article.id == article_id, Article.status == 2, Article.user_id == g.user_id) \
            .first()
        # .update({'title':title, 'article_content.content':content})

        if not data:
            return {'message': "Access Violation", 'data': None}, 403

        data.title = title
        data.article_content.content = content
        #
        # db.session.add(data)
        db.session.commit()

        return {'article': data.id, 'title': data.title, "uptime": data.utime.isoformat()}, 201

    def delete(self, article_id):

        try:
            # 根据文章id，作者id是否是用户id 查询数据
            data = Article.query.options(load_only(Article.id)). \
                filter(Article.id == article_id, Article.status == 2, Article.user_id == g.user_id) \
                .delete()

            db.session.commit()
            return {"message": "OK", "data": None}

        except Exception as e:
            db.session.rollback()
            print('文章删除失败')
            print(e)
            return {'message': "Access Violation", 'data': None}, 403


"""创建文章主类"""


class CreateArticleResource(Resource):
    method_decorators = {'post': [login_required]}

    def post(self):
        """创建文章"""
        parser = RequestParser()
        parser.add_argument('category_id', required=True, location='form', type=int)
        parser.add_argument('area_id', required=True, location='form', type=int)
        parser.add_argument('title', required=True, location='form', type=str)
        # parser.add_argument('cover', required=True, location='json', type=str)
        parser.add_argument('content', required=True, location='form', type=str)
        parser.add_argument('photo', type=image_file, location='files', action='append')

        # 获取参数
        args = parser.parse_args()
        user_id = g.user_id

        category_id = args.category_id
        area_id = args.area_id
        title = args.title
        content = args.content
        upload_files = args.photo

        # print(upload_files)
        # input("-------------")
        cover_dict = {}

        if upload_files:
            # key的值
            index_num = 0
            # 图片字典
            for img_file in upload_files:
                # 读取二进制数据
                img_bytes = img_file.read()
                index_num += 1
                try:
                    file_url = upload_file(img_bytes)
                    # 添加到 图片字典中
                    cover_dict[str(index_num)] = file_url
                except BaseException as e:
                    return {'message': 'thired Error: %s' % e, 'data': None}, 500

        try:
            # 存入数据库
            article = Article(category_id=category_id, user_id=user_id, area_id=area_id, title=title, cover=cover_dict)
            print('存储文章基本信息')
            db.session.add(article)
            # 先执行插入插入操作， 才能获取article 的id
            db.session.flush()
            if article.category.cate_name == '游记':
                article.user.travel_note_num += 1
            else:
                # 话题,求助，活动 则 发帖数 +1
                article.user.note_num += 1

            print('存储文章内容')

            art_content = ArticleContent(article_id=article.id, content=content)
            db.session.add(art_content)
            db.session.commit()
            # 删除缓存
            usercache = UserCache(user_id)
            usercache.clear()

            wc = WeatherCache(areaid=area_id)
            wc.clear()

            rest = {'article': article.id,
                    'title': article.title,
                    'time': article.ctime.isoformat(),
                    'cover': article.cover,
                    }

            return rest, 201

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

"""点赞游记主类"""


class LikeArticleResource(Resource):
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
            # 清除 redis中的文章 缓存
            wc = WeatherCache(areaid=like_model.article.area_id)
            wc.clear()

            return {'liker_id': g.user_id, 'art_id': art_id, 'time': like_model.utime.isoformat()}, 201

        except Exception as e:
            print("点赞游记操作失败， ")
            print(e)
            db.session.rollback()
            return {"message": '操作失败！', 'data': None}, 400


"""点赞用户主类"""


class LikeUserResource(Resource):
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

            # 清除缓存
            usercache = UserCache(user_id)
            usercache.clear()

            return {'liker_id': g.user_id, 'liked_id': user_id, 'time': like_model.utime.isoformat()}, 201

        except Exception as e:
            print("点赞用户操作失败， ")
            print(e)
            db.session.rollback()
            return {"message": '操作失败！', 'data': None}, 400


"""点赞评论主类"""


class LikeCommentResource(Resource):
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


"""点踩游记 or 评论 主类"""


class DisLikeArticleResource(Resource):
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


class AreaArtilceLikeDetail(Resource):
    """根据地区id，查询用户点赞的情况"""
    method_decorators = [login_required]

    def get(self):
        parser = RequestParser()
        parser.add_argument('area_id', required=True, location='args', type=int)
        parser.add_argument('cate_id', required=True, location='args', type=int)

        # 获取 参数 area_id
        args = parser.parse_args()
        area_id = args.area_id  # 地区id
        cate_id = args.cate_id  # 分类id

        print(cate_id)
        print(area_id)
        # 用户ID
        user_id = g.user_id

        # 根据area_id

        try:

            area_modle = Area.query.options(load_only(Area.id)).filter(Area.id == area_id).first()

            # 游记的id 为 6
            # category_id == 6
            art_list = area_modle.articles.filter(Article.status == Article.STATUS.APPROVED,
                                                  Article.category_id == cate_id).all()

            rest = []
            for item in art_list:
                # 判断用户对此文章点赞没
                if item.like_lists.filter(LikeComment.liker_id == user_id, LikeComment.relation == 1).all():
                    # 添加文章id
                    rest.append(item.id)

            return rest

        except Exception as e:
            print('数据库 查询文章地区点赞 失败')
            print(e)
            print(1222222222222222)
            return {"message": "非法 访问"}, 400


def auto_data():
    """自动填充数据库"""

    area_list = db.session.query(Area).filter(Area.parent_id == 0).all()
    # print(area_list)
    print(11111111111)

    # print(area_list[33].subs.all()[0].area_name)

    # 用户id list
    user_list = [1, 2, 4]

    # 分类id list
    cate_list = [1, 2, 3, 4, 5, 6]

    for area in area_list:

        sub_model_list = area.subs.all()
        # 创建 澳门，香港，台湾 数据
        if len(sub_model_list) == 0:
            art_list = []
            # 创建 澳门，香港，台湾 数据
            for i in range(10):
                art_list.append(Article(category_id=cate_list[0],
                                        user_id=user_list[0], area_id=area.id,
                                        title="测试数据-{}话题".format(area.area_name)))
                art_list.append(Article(category_id=cate_list[1],
                                        user_id=user_list[0], area_id=area.id,
                                        title="测试数据-{}求助".format(area.area_name)))
                art_list.append(Article(category_id=cate_list[2],
                                        user_id=user_list[0], area_id=area.id,
                                        title="测试数据-{}活动".format(area.area_name)))
                art_list.append(Article(category_id=cate_list[3],
                                        user_id=user_list[0], area_id=area.id,
                                        title="测试数据-{}公告".format(area.area_name)))
                art_list.append(Article(category_id=cate_list[4],
                                        user_id=user_list[0], area_id=area.id,
                                        title="测试数据-{}商家".format(area.area_name)))
                art_list.append(Article(category_id=cate_list[5],
                                        user_id=user_list[0], area_id=area.id,
                                        title="测试数据-{}游记".format(area.area_name)))

            spe = Special(area_id=area.id, spe_intr="介绍%s---测试数据" % (area.area_name),
                          spe_cultural="特色文化%s----测试数据" % (area.area_name),
                          spe_scenery="特色美景%s----测试数据" % (area.area_name),
                          spe_snack="特色小吃%s----测试数据" % (area.area_name))

            db.session.add_all(art_list)
            db.session.add(spe)
            db.session.flush()
            content = []
            for article in art_list:
                if article.category.cate_name == '游记':
                    article.user.travel_note_num += 1
                else:
                    article.user.note_num += 1

                content.append(ArticleContent(article_id=article.id, content="测试数据-{}".format(area.area_name)))
                # input('循环文章')

            db.session.add_all(content)
            db.session.commit()
            # input('存储到数据库，文章内容')
            # 执行完跳过此循环
            # print(area.area_name)
            continue

        #
        if len(sub_model_list) == 1:
            # 判断只到 区级
            # print(sub_model_list)
            # input('等待')
            sub_model_list = sub_model_list[0].subs.all()

            if sub_model_list[0].area_name == '市辖区':
                sub_model_list = sub_model_list[1:]

        if sub_model_list[0].area_name == '市辖区':
            sub_model_list = sub_model_list[1:]

        # print(sub_model_list)
        # input('等待')
        for area in sub_model_list:

            art_list = []
            # print(area.area_name)
            for i in range(10):
                art_list.append(Article(category_id=cate_list[0],
                                        user_id=user_list[0], area_id=area.id,
                                        title="测试数据-{}话题".format(area.area_name)))
                art_list.append(Article(category_id=cate_list[1],
                                        user_id=user_list[0], area_id=area.id,
                                        title="测试数据-{}求助".format(area.area_name)))
                art_list.append(Article(category_id=cate_list[2],
                                        user_id=user_list[0], area_id=area.id,
                                        title="测试数据-{}活动".format(area.area_name)))
                art_list.append(Article(category_id=cate_list[3],
                                        user_id=user_list[0], area_id=area.id,
                                        title="测试数据-{}公告".format(area.area_name)))
                art_list.append(Article(category_id=cate_list[4],
                                        user_id=user_list[0], area_id=area.id,
                                        title="测试数据-{}商家".format(area.area_name)))
                art_list.append(Article(category_id=cate_list[5],
                                        user_id=user_list[0], area_id=area.id,
                                        title="测试数据-{}游记".format(area.area_name)))

            # 排除 已存在数据
            if area.id == 951211:
                continue

            spe = Special(area_id=area.id, spe_intr="介绍%s---测试数据" % (area.area_name),
                          spe_cultural="特色文化%s----测试数据" % (area.area_name),
                          spe_scenery="特色美景%s----测试数据" % (area.area_name),
                          spe_snack="特色小吃%s----测试数据" % (area.area_name))

            db.session.add_all(art_list)
            db.session.add(spe)
            db.session.flush()
            content = []
            for article in art_list:
                if article.category.cate_name == '游记':
                    article.user.travel_note_num += 1
                else:
                    article.user.note_num += 1

                content.append(ArticleContent(article_id=article.id, content="测试数据-{}".format(area.area_name)))

            db.session.add_all(content)
            db.session.commit()


"""特色文章"""


class SpecialResource(Resource):
    method_decorators = {"post": [login_required]}

    def get(self):
        parser = RequestParser()
        parser.add_argument('area_id', required=True, location='args', type=int)
        parser.add_argument('type', location='args', type=str)
        # 获取参数
        args = parser.parse_args()
        area_id = args.area_id
        flag = args.type



        try:

            if flag == 'user':
                print('用户特色')
                # 数据库查询
                spe_mod = Special.query.options(load_only(Special.id)).filter(Special.area_id == area_id,Special.user_id.isnot(None)).all()

            else:
                # 数据库查询
                spe_mod = Special.query.options(load_only(Special.id)).filter(Special.area_id == area_id).all()

        except Exception as e:
            print('特色 数据库查询失败')
            print(e)
            return {"message": '查询失败！', 'data': None}, 401


        if spe_mod != []:
            if len(spe_mod) >= 1:
                rest = [item.to_dict() for item in spe_mod]
                return {"message": "OK", "data": rest}

            return {"message": "OK", "data": spe_mod.to_dict()}
        else:
            return {"message": '查询失败！', 'data': None}



    def post(self):
        """创建特色"""
        parser = RequestParser()
        parser.add_argument('spe_intr', location='form', type=str)
        parser.add_argument('spe_cultural', location='form', type=str)
        parser.add_argument('spe_scenery', location='form', type=str)
        parser.add_argument('spe_snack', location='form', type=str)
        parser.add_argument('area_id', required=True, location='form', type=str)
        parser.add_argument('intr_photo', type=image_file, location='files', action='append')
        parser.add_argument('cultural_photo', type=image_file, location='files', action='append')
        parser.add_argument('scenery_photo', type=image_file, location='files', action='append')
        parser.add_argument('snack_photo', type=image_file, location='files', action='append')
        parser.add_argument('snack_photo', type=image_file, location='files', action='append')
        parser.add_argument('story_photo', type=image_file, location='files', action='append')
        parser.add_argument('title', required=True, location='form', type=str)
        parser.add_argument('story', location='form', type=str)
        parser.add_argument('action', type=str, location='form')
        print('11111111111111111111111')
        # 获取参数
        args = parser.parse_args()
        spe_intr = args.spe_intr
        spe_cultural = args.spe_cultural
        spe_scenery = args.spe_scenery
        spe_snack = args.spe_snack
        area_id = args.area_id
        intr_photo = args.intr_photo
        cultural_photo = args.cultural_photo
        scenery_photo = args.scenery_photo
        snack_photo = args.snack_photo
        story_photo = args.story_photo
        title = args.title
        story = args.story
        user_id = g.user_id

        print('获取到的参数')

        # input('等待》》》》》》》》》》》')
        # 图片字典
        intr_dict = {}
        if intr_photo:  # 判断 特色 简介图片是否存在
            # key的值
            index_num = 0

            for img_file in intr_photo:
                # 读取二进制数据
                img_bytes = img_file.read()
                index_num += 1
                try:
                    file_url = upload_file(img_bytes)
                    # 添加到 图片字典中
                    intr_dict[str(index_num)] = file_url
                except BaseException as e:
                    return {'message': 'thired Error: %s' % e, 'data': None}, 400
        # 图片字典
        cult_dict = {}
        if cultural_photo:  # 判断 特色 文化图片是否存在
            # key的值
            index_num = 0

            for img_file in cultural_photo:
                # 读取二进制数据
                img_bytes = img_file.read()
                index_num += 1
                try:
                    file_url = upload_file(img_bytes)
                    # 添加到 图片字典中
                    cult_dict[str(index_num)] = file_url
                except BaseException as e:
                    return {'message': 'thired Error: %s' % e, 'data': None}, 400

        # 图片字典
        scenery_dict = {}
        if scenery_photo:  # 判断 特色 美景图片是否存在
            # key的值
            index_num = 0

            for img_file in scenery_photo:
                # 读取二进制数据
                img_bytes = img_file.read()
                index_num += 1
                try:
                    file_url = upload_file(img_bytes)
                    # 添加到 图片字典中
                    scenery_dict[str(index_num)] = file_url
                except BaseException as e:
                    return {'message': 'thired Error: %s' % e, 'data': None}, 400

        # 图片字典
        snack_dict = {}
        if snack_photo:  # 判断 特色 小吃图片是否存在
            # key的值
            index_num = 0

            for img_file in snack_photo:
                # 读取二进制数据
                img_bytes = img_file.read()
                index_num += 1
                try:
                    file_url = upload_file(img_bytes)
                    # 添加到 图片字典中
                    snack_dict[str(index_num)] = file_url
                except BaseException as e:
                    return {'message': 'thired Error: %s' % e, 'data': None}, 400

        story_dict = {}
        if story_photo:  # 判断 特色 小吃图片是否存在
            # key的值
            index_num = 0

            for img_file in story_photo:
                # 读取二进制数据
                img_bytes = img_file.read()
                index_num += 1
                try:
                    file_url = upload_file(img_bytes)
                    # 添加到 图片字典中
                    story_dict[str(index_num)] = file_url
                except BaseException as e:
                    return {'message': 'thired Error: %s' % e, 'data': None}, 400

        # 查询 数据库中是否存有数据
        spe = Special.query.options(load_only(Special.id)). \
            filter(Special.area_id == area_id, Special.user_id == user_id).first()

        if spe:
            spe.spe_intr = spe_intr
            spe.spe_cultural = spe_cultural
            spe.spe_scenery = spe_scenery
            spe.spe_snack = spe_snack
            spe.intr_photo = intr_dict
            spe.cultural_photo = cult_dict
            spe.scenery_photo = scenery_dict
            spe.snack_photo = snack_dict
            spe.story_photo = story_dict
            spe.spe_title = title
            spe.story = story
        else:
            # 存入数据库
            spe = Special(area_id=area_id, spe_intr=spe_intr, spe_cultural=spe_cultural, spe_scenery=spe_scenery,
                          spe_snack=spe_snack, intr_photo=intr_dict, cultural_photo=cult_dict, user_id=user_id,
                          story_photo=story_dict,
                          scenery_photo=scenery_dict, snack_photo=snack_dict, spe_title=title, story=story)

        try:
            # 提交
            db.session.add(spe)
            db.session.commit()
        except Exception as e:
            print('特色，数据库，创建失败')
            print(e)
            db.session.rollback()
            return {"message": '创建失败！', "data": None}, 401

        return {"message": "OK", "data": spe.to_dict()}
