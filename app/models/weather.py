from app import db
from utils.my_model import TimeBaseModel


# class Weather(db.Model, TimeBaseModel):
#     """天气表"""
#     __tablename__ = 'tb_weather'
#
#     id = db.Column(db.Integer, primary_key=True, doc='天气ID')
#     area_id = db.Column(db.Integer, db.ForeignKey("tb_area.id"), doc='地区id')
#     Tmax = db.Column(db.Integer, doc='最高温度')
#     lowest = db.Column(db.Integer, doc='对低温度')
#     weather = db.Column(db.String(128), doc='天气')
#
#

