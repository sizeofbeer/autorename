import flask_restful
from flask_restful import request
from functools import wraps
from .models import UserInfor

def authenticate(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        returnData = {
            'status': 0,
            'msg': ''
        }
        try:
            endpoint = request.endpoint  # 接口
            print('接口:', endpoint)
            # return func(*args, **kwargs) # 全部通过
            if endpoint and (endpoint == 'login'):  # 如果是登录接口
                return func(*args, **kwargs)

            header = request.headers
            token = header.get('token')
            if not token:   # 请求没带Token拒绝执行
                returnData['status'] = 2
                returnData['msg'] = '请求未携带token!'
                return returnData

            user = check_token(token)   # 检查Token合法
            if not user:
                returnData['status'] = 2
                returnData['msg'] = 'token已失效!'
                return returnData

            if user.Role == 'superAdmin':    # 超级管理员跳过接口权限检查
                return func(*args, **kwargs)

            returnData['msg'] = '无查询权限!'
            return returnData
        except Exception as error:
            returnData['msg'] = str(error)
            return returnData
    return wrapper

def check_token(token): # 检查Token是否合法
    return UserInfor.verify_auth_token(token)

class AuthResource(flask_restful.Resource):  # Resource类继承,增加权限校验方法
    method_decorators = [authenticate]   # applies to all inherited resources