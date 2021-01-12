from flask_restful import Resource, fields, marshal_with
import datetime
from flask import request
from sqlalchemy import and_, not_
from .parsers import search_post_parser, add_post_parser, author_post_parser
from apps.auth.models import AuthorKey, db
from apps.store.models import ClientBaseConfigure, ModelInfor, WarehouseInfor
from apps.store.actions import save_file, split_by_token


common_fields = {
    'status': fields.Integer(default=0),
    'msg': fields.String()
}

config_fields = {
    'ID': fields.Integer(),
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
    'msg': fields.String(default='状态配置/查询成功!')
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
            pass_tag, args = search_post_parser.parse_args() # strict=True, 不允许有额外参数
            if not pass_tag: # 参数验证不通过(名称、类型、数据结构)
                return {'msg': args}

            ID = args['ID']
            machineCode = args['machineCode']

            res = ClientBaseConfigure.query.filter(and_( # 查询未完成情况
                ClientBaseConfigure.ID==ID,
                not_(ClientBaseConfigure.ProcessState == "Finish"),
            )).first()

            if not res:
                return {'msg': '该ID下无配置信息!'}

            if res.machineCode != machineCode: # 机器码不匹配
                return {'msg': "授权码已注册!"}

            if res.ProcessState == 'Waiting':
                ClientBaseConfigure.query.filter_by(index=res.index).update({ # 更新配置
                    'ProcessState': 'Doing',
                })
                db.session.commit()

            upload_file = request.files['file'] # 图片
            is_success, image = save_file(upload_file, res.BatchID) # 是否保存成功
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

            ID = args['ID']
            Path = args['Path']
            YearMonth = args['YearMonth']
            Warehouse = args['Warehouse']
            deltag = args['deltag']
            picname = args['picname']
            ModelPaper = args['ModelPaper']

            res = AuthorKey.query.filter_by(ID=ID).first()
            if not res: # 查不到授权码
                return {'status': 0, 'msg': "无效授权码!"}
            if res.machineCode is None: # 未绑定机器
                return {'status': 0, 'msg': "授权码未注册, 请绑定机器!"}
            
            res = ClientBaseConfigure.query.filter(and_( # 查询未完成情况
                ClientBaseConfigure.ID==ID,
                not_(ClientBaseConfigure.ProcessState == "Finish"),
            )).first()
            if not res:
                return {'status': 0, 'msg': '客户端程序异常!'}

            if res.ProcessState == 'Doing':
                return {'status': 0, 'msg': '参数配置失败! 原因: 系统正在上传数据, 暂无法进行参数配置!'}
            
            ClientBaseConfigure.query.filter_by(index=res.index).update({ # 更新配置
                'Path': Path,
                'YearMonth': YearMonth,
                'Warehouse': Warehouse,
                'deltag': deltag,
                'picname': picname,
            })
            db.session.commit()

            if Role != "user": # 管理员更新模板
                ClientBaseConfigure.query.filter_by(index=res.index).update({
                    'ModelPaper': ModelPaper,
                })
                db.session.commit()

            res = ClientBaseConfigure.query.filter_by(index=res.index).first() # 查询最新配置信息
            return res
        except Exception as error:
            return {'status': 0, 'msg': str(error)}

class ClientParamConfig(Resource): # exe程序修改配置
    
    @marshal_with(config_fields)
    def post(self):
        try:
            # 获取请求参数
            pass_tag, args = add_post_parser.parse_args() # strict=True, 不允许有额外参数
            if not pass_tag: # 参数验证不通过(名称、类型、数据结构)
                return {'status': 0, 'msg': args}

            ID = args['ID']
            PathTag = args['PathTag']
            ProcessState = args['ProcessState']
            picname = args['picname']

            res = AuthorKey.query.filter_by(ID=ID).first()
            if not res: # 查不到授权码
                return {'status': 0, 'msg': "无效授权码!"}
            if res.machineCode is None: # 未绑定机器
                return {'status': 0, 'msg': "授权码未注册, 请绑定机器!"}
            
            res = ClientBaseConfigure.query.filter(and_( # 查询未完成配置信息
                ClientBaseConfigure.ID==ID,
                not_(ClientBaseConfigure.ProcessState == "Finish"),
            )).first()

            if not res:
                return {'status': 0, 'msg': '该ID下无配置信息!'}

            ClientBaseConfigure.query.filter_by(index=res.index).update({ # 更新配置信息
                'PathTag': PathTag,
                'ProcessState': ProcessState,
                'picname': picname,
            })
            db.session.commit()

            res = ClientBaseConfigure.query.filter_by(index=res.index).first() # 查询最新信息
            return res
        except Exception as error:
            return {'status': 0, 'msg': str(error)}

class AuthorConfig(Resource):

    @marshal_with(common_fields)
    def post(self):
        try:
            pass_tag, args = author_post_parser.parse_args() # strict=True, 不允许有额外参数
            if not pass_tag: # 参数验证不通过(名称、类型、数据结构)
                return {'msg': args}

            ID = args['ID']
            machineCode = args['machineCode']

            res = AuthorKey.query.filter_by(ID=ID).first()
            if not res: # 查不到授权码
                return {'msg': "无效授权码!"}
            if res.machineCode is None:
                AuthorKey.query.filter_by(ID=ID).update({'machineCode': machineCode}) # 绑定授权码
                db.session.commit()
            else:
                if res.machineCode != machineCode: # 机器码不匹配
                    return {'msg': "授权码已注册!"}
            return {'status': 1, 'msg': "授权码注册成功!"}
        except Exception as error:
            return {'msg': str(error)}

class UpStatusSearch(Resource):
    
    @marshal_with(config_fields)
    def post(self):
        try:
            pass_tag, args = search_post_parser.parse_args() # strict=True, 不允许有额外参数
            if not pass_tag: # 参数验证不通过(名称、类型、数据结构)
                return {'status': 0, 'msg': args}

            ID = args['ID']

            res = AuthorKey.query.filter_by(ID=ID).first() # 授权码信息查询
            if not res: # 查不到授权码
                return {'status': 0, 'msg': "无效授权码!"}
            if res.machineCode is None: # 未绑定机器
                return {'status': 0, 'msg': "授权码未注册, 请绑定机器!"}

            res = ClientBaseConfigure.query.filter(and_( # 查询是否有未完成配置
                ClientBaseConfigure.ID==ID,
                not_(ClientBaseConfigure.ProcessState == "Finish"),
            )).first()

            if not res: # 如果没有, 初始化配置
                config = ClientBaseConfigure(
                    ID = ID,
                    ModelPaper = '',
                    Path = '',
                    YearMonth = '',
                    Warehouse = '',
                    BatchID = '',
                )
                db.session.add(config)
                db.session.commit()
            
                res = ClientBaseConfigure.query.filter(and_( # 查询当前是否有未完成配置
                    ClientBaseConfigure.ID==ID,
                    not_(ClientBaseConfigure.ProcessState == "Finish"),
                )).first()
                today = datetime.datetime.today().strftime("%Y-%m-%d")
                BatchID = today + '_' + str(res.index) # 批次号赋值, 2021-01-12_index

                ClientBaseConfigure.query.filter_by(index=res.index).update({'BatchID': BatchID}) # 批次号更新
                db.session.commit()

                res = ClientBaseConfigure.query.filter_by(index=res.index).first() # 查询最新配置信息
            return res
        except Exception as error:
            return {'status': 0, 'msg': str(error)}