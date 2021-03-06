# -*- coding: utf-8 -*-
# author: JK time:2021/12/24
from datetime import datetime

from app import db
from common.utils.my_model import TimeBaseModel


class User(db.Model):
    """用户基本信息"""

    __tablename__ = 'user_basic'
    __table_args__ = {"extend_existing": True}

    id = db.Column(db.Integer, primary_key=True, doc='用户ID')
    name = db.Column(db.String(20), unique=True, doc='昵称')
    mobile = db.Column(db.String(11), unique=True, nullable=False, doc='手机号')
    profile_photo = db.Column(db.String(256), doc='用户头像')
    is_admin = db.Column(db.Boolean, default=False, doc='是否为管理员')
    last_login = db.Column(db.DateTime, default=datetime.now, doc='最后登录的时间')
    create_time = db.Column(db.DateTime, default=datetime.now, doc='注册时间')
    introduction = db.Column(db.String(128), doc='简介')
    status = db.Column(db.Integer, default=1, doc='状态，是否可用，0-不可用，1-可用')
    business = db.Column(db.Integer, default=0, doc='认证，是否为商家，0不是，1-是')
    dianzan_num = db.Column(db.Integer, default=0, doc='获赞总数')
    travel_note_num = db.Column(db.Integer, default=0, doc='游记总数')
    note_num = db.Column(db.Integer, default=0, doc='发帖总数')
    dianliang_area_num = db.Column(db.Integer, default=0, doc='点亮地区数')
    last_area_id = db.Column(db.Integer, db.ForeignKey("tb_area.id"), doc='用户上次位置')
    last_area = db.relationship("Area", backref=db.backref('users', uselist=False), uselist=False)
    is_Certification = db.Column(db.Boolean, default=False, doc='身份认证，False没认证，True认证成功')
    def to_dict(self):
        """模型转字典, 用于序列化处理"""
        return {
            'id': self.id,
            'name': self.name,
            'mobile': self.mobile,
            'photo': self.profile_photo,
            'intro': self.introduction,
            'dianzan_count': self.dianzan_num,
            'note_num_count': self.note_num,
            'travel_note_count': self.travel_note_num,
            'dianliang_area_count': self.dianliang_area_num,
            'business': self.business,
            'last_address': self.last_area.area_name if self.last_area else None,
            # 'like_comments': self.like_comments.
        }


class Address(db.Model, TimeBaseModel):
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


class UserProfile(db.Model, TimeBaseModel):
    """用户资料表"""
    __tablename__ = 'user_profile'
    __table_args__ = {"extend_existing": True}

    user_id = db.Column(db.Integer, db.ForeignKey("user_basic.id"), primary_key=True, doc='用户ID')
    email = db.Column(db.String(20), doc='邮箱')
    gender = db.Column(  # 性别
        db.Enum(
            "MAN",  # 男
            "WOMAN"  # 女
        ),
        default="MAN"
    )
    age = db.Column(db.Integer, doc='年龄')
    default_address_id = db.Column(db.Integer, db.ForeignKey("tb_address.id"), nullable=True, doc='用户常住地址')
    default_address = db.relationship("Address", backref=db.backref('users_profile', uselist=False), uselist=False)
    user_basic = db.relationship("User", backref=db.backref('user_profile', uselist=False), uselist=False)

    def to_dict(self):
        return {
            "id": self.user_id,
            'name': self.user_basic.name,
            "email": self.email,
            "gender": self.gender,
            "age": self.age,
            "default_address": self.default_address_id
        }


class RouterCard(db.Model, TimeBaseModel):
    __tablename__ = "tb_router_card"
    id = db.Column(db.Integer, primary_key=True, doc='行程卡')
    user_id = db.Column(db.Integer, db.ForeignKey("user_basic.id"), doc='用户ID')
    arrive_time = db.Column(db.DateTime, doc='到达时间')
    area_id = db.Column(db.Integer, db.ForeignKey("tb_area.id"), doc='地址id')
    complete = db.Column(db.Boolean, default=False, doc='是否到达')
    user = db.relationship("User", backref=db.backref('router_card', lazy='dynamic'), uselist=False)
    area = db.relationship("Area", backref='router_card', uselist=False)

    def to_dict(self):
        return {
            "area_id": self.area_id,
            "area": self.area.area_name,
            "arrive_time": self.arrive_time.isoformat(),
            "comp_time": self.utime.isoformat(),
            "complete": self.complete
        }
