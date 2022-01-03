# -*- coding: utf-8 -*-
# author: JK time:2021/12/26

from app import db

class Area(db.Model):
    """地区"""

    ___tablename__ = 'tb_area'

    id = db.Column(db.Integer, primary_key=True, doc='地区id')
    name = db.Column(db.String(20), doc='名称')
    parent_id = db.Column(db.Integer, db.ForeignKey('area.id'), doc='上级行政区')
    parent = db.relationship('Area', remote_side=[id], backref=db.backref('subs'))  # 自关联
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'subs': self.subs
        }
