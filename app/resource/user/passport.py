# -*- coding: utf-8 -*-
# author: JK time:2021/12/24


from flask_restful import Resource



class SMSCodeResource(Resource):
    """获取短信验证码"""
    def get(self):
        return {'foo': 'get'}


