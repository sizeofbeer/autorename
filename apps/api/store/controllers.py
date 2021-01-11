from flask_restful import Resource, fields, marshal_with
from flask import request
from sqlalchemy import and_, not_
from .parsers import search_post_parser, add_post_parser
from apps.store.models import ClientBaseConfigure, ModelInfor, WarehouseInfor, db
from apps.store.actions import save_file, split_by_token


common_fields = {
    'status': fields.Integer(default=0),
    'msg': fields.String()
}

config_fields = {
    'IP': fields.String(),
    'ModelPaper': fields.String(),
    'Path': fields.String(),
    'PathTag': fields.Boolean(),
    'BatchID': fields.String(),
    'Wordless': fields.Boolean(),
    'ProcessState': fields.String(),
    'YearMonth': fields.String(),
    'Warehouse': fields.String(),
    'deltag': fields.Boolean(),
    'picname': fields.String(),
    'status': fields.Integer(default=1),
    'msg': fields.String(default='状态查询成功!')
}

class ModelSelect(Resource):
    returnData = {
        'status': fields.Integer(default=0),
        'Model': fields.List(fields.String()),
        'msg': fields.String()
    }

    @marshal_with(returnData)
    def post(self):
        try:
            res_list = ModelInfor.query.all() # 获取所有模板信息

            if not res_list:
                return {'msg': "暂无模板信息!"}

            return {'status': 1, 'msg': "模型获取成功!", 'Model': [res.Model for res in res_list]}
        except Exception as error:
            return {'msg': str(error)}

class WarehouseSelect(Resource):
    returnData = {
        'status': fields.Integer(default=0),
        'Warehouse': fields.List(fields.String()),
        'msg': fields.String()
    }

    @marshal_with(returnData)
    def post(self):
        try:
            res_list = WarehouseInfor.query.all() # 获取所有仓库信息
            if not res_list:
                return {'msg': "暂无仓库信息!"}

            return {'status': 1, 'msg': "模型获取成功!", 'Warehouse': [res.Warehouse for res in res_list]}
        except Exception as error:
            returnData['msg'] = str(error)
            return returnData
        return returnData

class PicUpload(Resource):
    @marshal_with(common_fields)
    def post(self):
        try:
            upload_file = request.files['file'] # 图片
            is_success, image = save_file(upload_file) # 是否保存成功
            if not is_success:
                return {'msg': '图片上传失败!'}
            return {'status': 1, 'msg': '图片上传成功!'}
        except Exception as error:
            return {'msg': str(error)}

class ParamConfig(Resource):
    @marshal_with(config_fields)
    def post(self):
        try:
            # 获取token
            token = request.headers.get('token')
            Role = split_by_token(token)
            if not Role: # token验证不通过
                return {'status': 0, 'msg': "token已失效!"}

            # 获取请求参数
            pass_tag, args = add_post_parser.parse_args() # strict=True, 不允许有额外参数
            if not pass_tag: # 参数验证不通过(名称、类型、数据结构)
                return {'status': 0, 'msg': args}

            IP = args['IP']
            res = ClientBaseConfigure.query.filter_by(IP=IP).first() # 查询该IP状态
            if not res:
                return {'status': 0, 'msg': '该IP下无配置信息!'}

            if Role == "user":
                pass
            else:
                pass

            returnData['status'] = 1
            returnData['msg'] = "参数配置成功!"
            return returnData
        except Exception as error:
            return {'status': 0, 'msg': str(error)}

class UpStatusSearch(Resource):
    
    @marshal_with(config_fields)
    def post(self):
        try:
            print(request.headers)
            print(request.remote_addr)
            pass_tag, args = search_post_parser.parse_args() # strict=True, 不允许有额外参数
            if not pass_tag: # 参数验证不通过(名称、类型、数据结构)
                return {'status': 0, 'msg': args}

            IP = args['IP']
            
            res = ClientBaseConfigure.query.filter(and_(
                ClientBaseConfigure.IP==IP,
                not_(ClientBaseConfigure.ProcessState == "Finish"),
            )).first()

            if not res:
                return {'status': 0, 'msg': "请先配置机器!"}
            return res
        except Exception as error:
            return {'status': 0, 'msg': str(error)}