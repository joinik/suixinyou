from app import db
from utils.my_model import TimeBaseModel

from app.models.comment import Comment


class Category(db.Model, TimeBaseModel):
    """文章分类"""
    __tablename__ = "tb_category"
    __table_args__ = {"extend_existing": True}

    id = db.Column(db.Integer, primary_key=True)  # 分类编号
    cate_name = db.Column(db.String(64), nullable=False)  # 分类名
    is_deleted = db.Column(db.Boolean, default=False, doc="逻辑删除")


class Article(db.Model, TimeBaseModel):
    """文章基本信息表"""
    __tablename__ = "article_basic"
    __table_args__ = {"extend_existing": True}

    class STATUS:
        DRAFT = 0  # 草稿
        UNREVIEWED = 1  # 待审核
        APPROVED = 2  # 审核通过
        FAILED = 3  # 审核失败
        DELETED = 4  # 已删除
        BANNED = 5  # 封禁

    id = db.Column(db.Integer, primary_key=True, doc="文章ID")
    user_id = db.Column(db.Integer, db.ForeignKey("user_basic.id"), doc="用户ID")
    category_id = db.Column(db.Integer, db.ForeignKey("tb_category.id"), doc="分类ID")
    area_id = db.Column(db.Integer, db.ForeignKey("tb_area.id"), doc="地区ID")

    title = db.Column(db.String(128), doc="文章标题")
    cover = db.Column(db.JSON, doc="封面")
    status = db.Column(db.Integer, default=2, doc="文章状态")
    reason = db.Column(db.String(256), doc="未通过原因")
    comment_count = db.Column(db.Integer, default=0, doc="评论数")
    like_count = db.Column(db.Integer, default=0, doc="点赞数")
    dislike_count = db.Column(db.Integer, default=0, doc="点踩数")

    # area = db.relationship("Area", backref=db.backref("articles", lazy="dynamic"), uselist=False)
    user = db.relationship("User", backref=db.backref("articles", lazy="dynamic"), uselist=False)
    category = db.relationship("Category", backref=db.backref("articles", lazy="dynamic"), uselist=False)
    area = db.relationship("Area", backref=db.backref("articles", lazy="dynamic"), uselist=False)
    # # 当前新闻的所有评论
    comments = db.relationship("Comment", backref=db.backref("article", uselist=False), lazy="dynamic")
    article_content = db.relationship("ArticleContent",
                                      backref=db.backref("articles", uselist=False, ),
                                      cascade="all, delete-orphan",
                                      # passive_deletes=True,
                                      # single_parent=True,
                                      uselist=False,
                                      )

    def to_dict(self):
        return {
            "cate_name": self.category.cate_name,
            "area_id": self.area.id,
            "area_name": self.area.area_name,
            "art_id": self.id,
            "title": self.title,
            "cover": self.cover,
            "pubdate": self.ctime.isoformat(),
            "update": self.utime.isoformat(),
            "aut_id": self.user.id,
            "aut_name": self.user.name,
            "aut_photo": self.user.profile_photo,
            "content": self.article_content.content,
            "comment_count": self.comment_count,
            "like_count": self.like_count,
            "dislike_count": self.dislike_count,
            "comment_list": [{
                "com_id": item.comment_id,
                "aut_id": item.user.id,
                "aut_name": item.user.name,
                "aut_photo": item.user.profile_photo,
                "pubdate": item.ctime.isoformat(),
                "content": item.content,
                "reply_count": item.reply_count,
                "like_count": item.like_count
            } for item in self.comments.filter(Comment.status == Comment.STATUS.APPROVED).limit(2)]
        }


class ArticleContent(db.Model):
    """
    文章内容表
    """
    __tablename__ = "tb_article_content"
    __table_args__ = {"extend_existing": True}

    # __table_args__ = {"extend_existing": True}
    # extend_existing = True
    article_id = db.Column(db.Integer, db.ForeignKey("article_basic.id", ondelete="CASCADE"), primary_key=True,
                           doc="文章ID")
    content = db.Column(db.Text, doc="帖文内容")


class Special(db.Model):
    """特色类"""

    __tablename__ = "tb_special"

    id = db.Column(db.Integer, primary_key=True, doc="特色主键")
    spe_intr = db.Column(db.String(256), doc="当地介绍")
    spe_cultural = db.Column(db.String(256), doc="文化特色")
    spe_scenery = db.Column(db.String(256), doc="美丽景色")
    spe_snack = db.Column(db.String(256), doc="特色小吃")
    intr_photo = db.Column(db.JSON, doc="介绍图片")
    cultural_photo = db.Column(db.JSON, doc="文化图片")
    scenery_photo = db.Column(db.JSON, doc="美景图片")
    snack_photo = db.Column(db.JSON, doc="小吃图片")
    spe_title = db.Column(db.String(128), doc="特色标题")    # 此字段 只有用户有
    story = db.Column(db.Text, doc='我的故事')               # 此字段 只有用户有
    story_photo = db.Column(db.JSON, doc='故事图片')         # 此字段 只有用户有
    area_id = db.Column(db.Integer, db.ForeignKey("tb_area.id"), nullable=False, doc="地区ID")
    user_id = db.Column(db.Integer, db.ForeignKey("user_basic.id", ondelete="CASCADE"), doc="用户ID")
    user = db.relationship("User", backref=db.backref("special", lazy="dynamic", cascade="all, delete-orphan"),
                           uselist=False)

    def to_dict(self):
        return {
            "area_id": self.area_id,
            "aut_id": self.user_id,
            "aut_name": self.user.name if self.user_id else None,
            "spe_title": self.spe_title,
            "story": self.story,
            "spe_intr": self.spe_intr,
            "spe_cultural": self.spe_cultural,
            "spe_scenery": self.spe_scenery,
            "spe_snack": self.spe_snack,
            "intr_photo": self.intr_photo,
            "cultural_photo": self.cultural_photo,
            "scenery_photo": self.scenery_photo,
            "snack_photo": self.snack_photo
        }
