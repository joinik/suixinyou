



#
from datetime import datetime

from app import db
from common.utils.my_model import TimeBaseModel


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

    comment_id = db.Column(db.Integer, primary_key=True, doc='评论ID')
    user_id = db.Column(db.Integer, db.ForeignKey("user_basic.id"),nullable=False, doc='用户ID')
    article_id = db.Column(db.Integer, db.ForeignKey("article_basic.id"),nullable=False, doc='文章ID')
    parent_id = db.Column(db.Integer, db.ForeignKey("article_comment.comment_id"), doc='父评论id')

    like_count = db.Column(db.Integer, default=0, doc='点赞数')
    reply_count = db.Column(db.Integer, default=0, doc='回复数')
    content = db.Column(db.String(200), nullable=False, doc='评论内容')
    ctime = db.Column(db.DateTime, default=datetime.now, doc='创建时间')
    is_top = db.Column(db.Boolean, default=False, doc='是否置顶')
    status = db.Column(db.Integer, default=1, doc='评论状态')
    user = db.relationship("User", backref="comments")

    # user = db.relationship("User", backref=db.backref('comments', lazy='dynamic'), uselist=False)
    # article = db.relationship("Article", backref='comments', uselist=False)
    # like_user = db.relationship("User",
    #                             secondary='tb_like',
    #                             lazy='dynamic',
    #                             backref='like_comment')
    # 实现对评论的回复（其实就是自关联）
    parent = db.relationship("Comment", remote_side=comment_id)  # 自关联


#
class LikeComment(db.Model, TimeBaseModel):
    """点赞表"""
    __tablename__ = 'tb_like'
    __table_args__ = {"extend_existing": True}
    id = db.Column(db.Integer, primary_key=True, doc='点赞id')
    liker_id = db.Column(db.Integer, db.ForeignKey("user_basic.id"), doc='点赞用户ID')
    article_id = db.Column(db.Integer, db.ForeignKey("article_basic.id"), doc='文章ID')
    comment_id = db.Column(db.Integer, db.ForeignKey("article_comment.comment_id"), doc='评论ID')
    liked_id = db.Column(db.Integer, db.ForeignKey("user_basic.id"), doc='被点赞用户ID')
    relation = db.Column(db.Integer, default=1, doc='关系，0-取消，1-点赞')

    # 一对一关系 uselist = False 返回一个对象，反之一个对象列表
    # 查看用户点赞的情况
    liker = db.relationship("User", backref=db.backref('like_lists', lazy='dynamic'),
                            foreign_keys=[liker_id],
                           uselist=False)
    # # 查看用户有谁对他点赞
    liked = db.relationship("User", backref=db.backref('likers', lazy='dynamic'),
                            foreign_keys=[liked_id],
                           uselist=False)
    article = db.relationship("Article", foreign_keys=[article_id], backref=db.backref('like_lists', lazy='dynamic'), uselist=False)
    comment = db.relationship("Comment", foreign_keys=[comment_id], backref=db.backref('like_lists', lazy='dynamic'), uselist=False)


class DisLikeComment(db.Model, TimeBaseModel):
    """点踩表"""
    __tablename__ = 'tb_dislike'
    __table_args__ = {"extend_existing": True}

    id = db.Column(db.Integer, primary_key=True, doc='点踩ID')
    disliker_id = db.Column(db.Integer, db.ForeignKey("user_basic.id"), doc='点踩用户ID')
    article_id = db.Column(db.Integer, db.ForeignKey("article_basic.id"), doc='文章ID')
    comment_id = db.Column(db.Integer, db.ForeignKey("article_comment.comment_id"), doc='评论ID')
    disliked_id = db.Column(db.Integer, db.ForeignKey("user_basic.id"), doc='被点踩用户ID')
    relation = db.Column(db.Integer, default=1, doc='关系，0-取消，1-点赞')

    disliker = db.relationship("User", backref=db.backref('dislike_lists', lazy='dynamic'),
                            foreign_keys=[disliker_id],
                            uselist=False)
    # 一对一关系 uselist = False 返回一个对象，反之一个对象列表
    disliked = db.relationship("User", backref=db.backref('dislikers', lazy='dynamic'),
                            foreign_keys=[disliked_id],
                            uselist=False)
    article = db.relationship("Article", foreign_keys=[article_id], backref=db.backref('dislike_lists', lazy='dynamic'),
                              uselist=False)
    comment = db.relationship("Comment", foreign_keys=[comment_id], backref=db.backref('dislike_lists', lazy='dynamic'),
                              uselist=False)


