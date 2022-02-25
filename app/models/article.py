from app import db
from utils.my_model import TimeBaseModel


class Category(db.Model, TimeBaseModel):
    """文章分类"""
    __tablename__ = "tb_category"
    __table_args__ = {"extend_existing": True}

    id = db.Column(db.Integer, primary_key=True)  # 分类编号
    cate_name = db.Column(db.String(64), nullable=False)  # 分类名
    is_deleted = db.Column(db.Boolean, default=False, doc='逻辑删除')


class Article(db.Model, TimeBaseModel):
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
    status = db.Column(db.Integer, default=2, doc='文章状态')
    reason = db.Column(db.String(256), doc='未通过原因')
    comment_count = db.Column(db.Integer, default=0, doc='评论数')
    like_count = db.Column(db.Integer, default=0, doc='点赞数')
    dislike_count = db.Column(db.Integer, default=0, doc='点踩数')

    # area = db.relationship("Area", backref=db.backref('articles', lazy='dynamic'), uselist=False)
    user = db.relationship("User", backref=db.backref('articles', lazy='dynamic'), uselist=False)
    category = db.relationship('Category', backref=db.backref('articles', lazy='dynamic'), uselist=False)
    area = db.relationship('Area', backref=db.backref('articles', lazy='dynamic'), uselist=False)
    # category = db.relationship('Category', backref=db.backref('articles', lazy='dynamic'), uselist=False)
    # # 当前新闻的所有评论
    comments = db.relationship("Comment", backref=db.backref('article', uselist=False), lazy="dynamic")
    article_content = db.relationship("ArticleContent",
                                      backref=db.backref('articles', uselist=False), uselist=False)



    def todict(self):
        return {
            'cate_name': self.category.cate_name,
            'area_id': self.area.id,
            'area_name': self.area.area_name,
            'art_id': self.id,
            'title': self.title,
            'pubdate': self.ctime.isoformat(),
            'update': self.utime.isoformat(),
            'aut_id': self.user.id,
            'aut_name': self.user.name,
            'aut_photo': self.user.profile_photo,
            'content': self.article_content.content,
            'comment_count': self.comment_count,
            'like_count': self.like_count,
            'dislike_count': self.dislike_count
        }


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




