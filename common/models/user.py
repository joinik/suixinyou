# -*- coding: utf-8 -*-
# author: JK time:2021/12/24
from datetime import datetime

from app import db
from models.area import Area
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    """用户基本信息"""
    __tablename__ = 'tb_user_basic'

    id = db.Column(db.Integer, primary_key=True, doc='用户ID')
    name = db.Column(db.String(20), unique=True, doc='昵称')
    profile_photo = db.Column(db.String(256), doc='用户头像')
    mobile = db.Column(db.String(11), unique=True, nullable=False, doc='手机号')
    password_hash = db.Column(db.String(128), nullable=False)  # 加密的密码
    email = db.Column(db.String(20), doc='邮箱')
    gender = db.Column(  # 性别
        db.Enum(
            "MAN",  # 男
            "WOMAN"  # 女
        ),
        default="MAN"
    )
    age = db.Column(db.Integer, doc='年龄')
    dianzan_num = db.Column(db.String(20), default='0', doc='获赞总数')
    travel_note_num = db.Column(db.String(20), default='0', doc='游记总数')
    dianliang_area_num = db.Column(db.String(20), default='0', doc='点亮地区数')
    create_time = db.Column(db.DateTime, default=datetime.now)  # 注册时间
    last_login = db.Column(db.DateTime, default=datetime.now, doc='最后登录的时间')
    introduction = db.Column(db.String(128), doc='简介')
    is_admin = db.Column(db.Boolean, default=False, doc='是否为管理员')
    is_deleted = db.Column(db.Boolean, default=False, doc='逻辑删除')
    default_address_id = db.Column(db.Integer, db.ForeignKey("tb_address.id"), nullable=True, doc='用户常住地址')
    last_address_id = db.Column(db.Integer, db.ForeignKey("area.id"), nullable=True, doc='用户上次位置')
    default_address = db.relationship('Address', backref=db.backref('address'))

    def to_dict(self):
        """模型转字典, 用于序列化处理"""

        return {
            'id': self.id,
            'name': self.name,
            'photo': self.profile_photo,
            'age': self.age,
            'gender': self.gender,
            'intro': self.introduction,
            'dianzan_count': self.dianzan_num,
            'travel_note_count': self.travel_note_num,
            'dianliang_area_count': self.dianliang_area_num
        }



    def hash_password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

class Address(db.Model):
    """地址表"""

    __tablename__ = "tb_address"

    id = db.Column(db.Integer, primary_key=True, doc='地址ID')
    title = db.Column(db.String(20), doc='地址名称')
    province_id = db.Column(db.Integer, db.ForeignKey('area.id'), doc='省')
    city_id = db.Column(db.Integer, db.ForeignKey('area.id'), doc='市')
    district_id = db.Column(db.Integer, db.ForeignKey('area.id'), doc='区')
    province = db.relationship('Area', foreign_keys = [province_id], backref=db.backref('province_address'), uselist=False)
    city = db.relationship('Area', foreign_keys = [city_id], backref=db.backref('city_address'),  uselist=False )
    district = db.relationship('Area',  foreign_keys = [district_id], backref=db.backref('district_address'),  uselist=False )
    place = db.Column(db.String(50), doc='地址')
    id_deleted = db.Column(db.Boolean, default=False, doc='逻辑删除')


