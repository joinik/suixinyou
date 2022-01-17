# -*- coding: utf-8 -*-
# author: JK time:2021/12/24
from datetime import datetime

from sqlalchemy import MetaData
from sqlalchemy.orm import foreign, remote

from app import db


class Area(db.Model):
    """地区"""

    __tablename__ = 'tb_area'
    __table_args__ = {"extend_existing": True}

    id = db.Column(db.Integer, primary_key=True, doc='地区id')
    area_name = db.Column(db.String(20), doc='地区名称')
    city_code = db.Column(db.String(12), nullable=True, doc='地区编码')
    city_level = db.Column(db.Integer, nullable=True, doc='地区级别')
    parent_id = db.Column(db.Integer, db.ForeignKey("tb_area.id"), nullable=True, doc='上级行政区')

    parent = db.relationship("common.models.user.Area",
                             primaryjoin=('tb_area.c.id==tb_area.c.parent_id'),
                             remote_side=[id],
                             backref="subs",
                             # foreign_keys=[parent_id],
                             )
    # parent = db.relationship("common.models.user.Area", remote_side=[id])
    # parent = db.relationship("common.models.user.Area", remote_side=[id],
    #                          backref=db.backref('subs', remote_side='{}.id'.format("tb_area")))  # 自关联

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.area_name,
            # 'parent': self.parent.name if self.parent else self.parent,
            'city_level': self.city_level
        }


class User(db.Model):
    """用户基本信息"""

    __tablename__ = 'user_basic'
    __table_args__ = {"extend_existing": True}

    id = db.Column(db.Integer, primary_key=True, doc='用户ID')
    name = db.Column(db.String(20), unique=True, doc='昵称')
    mobile = db.Column(db.String(11), unique=True, nullable=False, doc='手机号')
    profile_photo = db.Column(db.String(256), doc='用户头像')
    last_login = db.Column(db.DateTime, default=datetime.now, doc='最后登录的时间')
    create_time = db.Column(db.DateTime, default=datetime.now, doc='注册时间')
    introduction = db.Column(db.String(128), doc='简介')
    status = db.Column(db.Integer, default=1, doc='状态，是否可用，0-不可用，1-可用')
    business = db.Column(db.Integer, default=0, doc='认证，是否为商家，0不是，1-是')
    dianzan_num = db.Column(db.Integer, default=0, doc='获赞总数')
    travel_note_num = db.Column(db.Integer, default=0, doc='游记总数')
    dianliang_area_num = db.Column(db.Integer, default=0, doc='点亮地区数')
    last_address_id = db.Column(db.Integer, db.ForeignKey("tb_area.id"), doc='用户上次位置')

    # last_address = db.relationship("common.models.user.Area", backref='users', uselist=False)

    def to_dict(self):
        """模型转字典, 用于序列化处理"""
        return {
            'id': self.id,
            'name': self.name,
            'photo': self.profile_photo,
            'intro': self.introduction,
            'dianzan_count': self.dianzan_num,
            'travel_note_count': self.travel_note_num,
            'dianliang_area_count': self.dianliang_area_num,
            'business': self.business,
        }


class Address(db.Model):
    """地址表"""

    __tablename__ = "tb_address"

    __table_args__ = {"extend_existing": True}

    id = db.Column(db.Integer, primary_key=True, doc='地址ID')
    title = db.Column(db.String(20), doc='地址名称')
    province_id = db.Column(db.Integer, db.ForeignKey("tb_area.id"), doc='省')
    city_id = db.Column(db.Integer, db.ForeignKey("tb_area.id"), doc='市')
    district_id = db.Column(db.Integer, db.ForeignKey("tb_area.id"), doc='区')
    place = db.Column(db.String(50), doc='地址')
    id_deleted = db.Column(db.Boolean, default=False, doc='逻辑删除')


class UserProfile(db.Model):
    """用户资料表"""
    __tablename__ = 'user_profile'
    __table_args__ = {"extend_existing": True}
    # __table_args__ = {"useexisting": True}

    user_id = db.Column(db.Integer, primary_key=True, doc='用户ID')
    email = db.Column(db.String(20), doc='邮箱')
    gender = db.Column(  # 性别
        db.Enum(
            "MAN",  # 男
            "WOMAN"  # 女
        ),
        default="MAN"
    )
    age = db.Column(db.Integer, doc='年龄')
    is_admin = db.Column(db.Boolean, default=False, doc='是否为管理员')
    default_address_id = db.Column(db.Integer, db.ForeignKey("tb_address.id"), nullable=True, doc='用户常住地址')

    # default_address = db.relationship(Address, backref='users', uselist=False)
    # user = db.relationship(User, backref=db.backref('user_profile'), uselist=False)

    def to_dict(self):
        return {
            "id": self.user_id,
            "email": self.email,
            "gender": self.gender,
            "age": self.age,
            "default_address": self.default_address_id
        }


class Category(db.Model):
    """文章分类"""
    __tablename__ = "tb_category"
    __table_args__ = {"extend_existing": True}

    id = db.Column(db.Integer, primary_key=True)  # 分类编号
    cate_name = db.Column(db.String(64), nullable=False)  # 分类名
    ctime = db.Column(db.DateTime, default=datetime.now)  # 记录的创建时间
    utime = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)  # 记录的更新时间
    id_deleted = db.Column(db.Boolean, default=False, doc='逻辑删除')


#
#


class Article(db.Model):
    """文章基本信息表"""
    __tablename__ = 'article_basic'
    __table_args__ = {"extend_existing": True}

    class STATUS:
        DRAFT = 0  # 草稿
        UNREVIEWED = 1  # 待审核
        APPROVED = 2  # 审核通过
        FAILED = 3  # 审核失败
        DELETED = 4  # 已删除
        BANNED = 5  # 封禁

    id = db.Column(db.Integer, primary_key=True, doc='文章ID')
    user_id = db.Column(db.Integer, db.ForeignKey("user_basic.id"), doc='用户ID')
    category_id = db.Column(db.Integer, db.ForeignKey("tb_category.id"), doc='分类ID')
    area_id = db.Column(db.Integer, db.ForeignKey('tb_area.id'), doc='地区ID')

    title = db.Column(db.String(128), doc='文章标题')
    # cover = db.Column(db.JSON, doc='封面')
    ctime = db.Column(db.DateTime, default=datetime.now, doc='创建时间')
    utime = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)  # 记录的更新时间
    status = db.Column(db.Integer, default=2, doc='文章状态')
    reason = db.Column(db.String(256), doc='未通过原因')
    comment_count = db.Column(db.Integer, default=0, doc='评论数')
    like_count = db.Column(db.Integer, default=0, doc='点赞数')
    dislike_count = db.Column(db.Integer, default=0, doc='点踩数')

    # area = db.relationship("common.models.user.Area", backref='articles', uselist=False)
    # user = db.relationship("common.models.user.User", foreign_keys=[user_id],
    #                        primaryjoin=foreign(user_id) == remote(User.id),
    #                        backref='articles', uselist=False)
    # category = db.relationship('Category', backref='articles', uselist=False, doc='频道ID')
    # # 当前新闻的所有评论
    # comments = db.relationship("Comment", lazy="dynamic")
    # article_content = db.relationship("ArticleContent", backref='articles', uselist=False)



#
class ArticleContent(db.Model):
    """
    文章内容表
    """
    __tablename__ = 'tb_article_content'
    __table_args__ = {"extend_existing": True}

    # __table_args__ = {'extend_existing': True}
    # extend_existing = True
    article_id = db.Column(db.Integer, db.ForeignKey("article_basic.id"), primary_key=True, doc='文章ID')
    content = db.Column(db.Text, doc='帖文内容')


class Comment(db.Model):
    """
    文章评论
    """
    __tablename__ = 'article_comment'
    __table_args__ = {"extend_existing": True}

    class STATUS:
        UNREVIEWED = 0  # 待审核
        APPROVED = 1  # 审核通过
        FAILED = 2  # 审核失败
        DELETED = 3  # 已删除

    id = db.Column(db.Integer, primary_key=True, doc='评论ID')
    user_id = db.Column(db.Integer, db.ForeignKey("user_basic.id"), doc='用户ID')
    article_id = db.Column(db.Integer, db.ForeignKey("article_basic.id"), doc='文章ID')
    parent_id = db.Column(db.Integer, db.ForeignKey("article_comment.id"), doc='父评论id')

    like_count = db.Column(db.Integer, default=0, doc='点赞数')
    reply_count = db.Column(db.Integer, default=0, doc='回复数')
    content = db.Column(db.String(200), doc='评论内容')
    ctime = db.Column(db.DateTime, default=datetime.now, doc='创建时间')
    is_top = db.Column(db.Boolean, default=False, doc='是否置顶')
    status = db.Column(db.Integer, default=1, doc='评论状态')

    # user = db.relationship("User", backref='comments', uselist=False)
    # article = db.relationship("Article", backref='comments', uselist=False)
    # like_user = db.relationship("User",
    #                             secondary='tb_like',
    #                             lazy='dynamic',
    #                             backref='like_comment')
    # 实现对评论的回复（其实就是自关联）
    # parent = db.relationship("common.models.user.Comment", remote_side=id)  # 自关联


#
class LikeComment(db.Model):
    """点赞表"""
    __tablename__ = 'tb_like'
    __table_args__ = {"extend_existing": True}

    # __table_args__ = {'keep_existing': True}
    id = db.Column("like_id", db.Integer, primary_key=True, doc='点赞ID')
    user_id = db.Column(db.Integer, db.ForeignKey("user_basic.id"), doc='用户ID')
    article_id = db.Column(db.Integer, db.ForeignKey("article_basic.id"), doc='文章ID')
    comment_id = db.Column(db.Integer, db.ForeignKey("article_comment.id"), doc='评论ID')

    # 一对一关系 uselist = False 返回一个对象，反之一个对象列表
    # user = db.relationship(User, backref='like_comments', uselist=False)
    # article = db.relationship(Article, backref='like_comments', uselist=False)
    # comment = db.relationship(Comment, backref=db.backref('like_comments', lazy='dynamic'), lazy='dynamic')


class DisLikeComment(db.Model):
    """点踩表"""
    __tablename__ = 'tb_dislike'
    __table_args__ = {"extend_existing": True}

    id = db.Column(db.Integer, primary_key=True, doc='点踩ID')
    user_id = db.Column(db.Integer, db.ForeignKey("user_basic.id"), doc='用户ID')
    article_id = db.Column(db.Integer, db.ForeignKey("article_basic.id"), doc='文章ID')
    comment_id = db.Column(db.Integer, db.ForeignKey("article_comment.id"), doc='评论ID')
    # 一对一关系 uselist = False 返回一个对象，反之一个对象列表
    # user = db.relationship(User, backref=db.backref('dislike_comments'), uselist=False)
    # article = db.relationship(Article, backref=db.backref('dislike_comments'), uselist=False)
    # comment = db.relationship(Comment, backref=db.backref('dislike_comments'), uselist=False)
