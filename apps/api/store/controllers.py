from flask_restful import Resource, fields, marshal_with
import datetime
from .parsers import search_post_parser, add_post_parser, author_post_parser
from apps.store.models import ModelInfor, WarehouseInfor, db
from apps.auth.models import ClientBaseConfigure


common_fields = {
    'status': fields.Integer(default=0),
    'msg': fields.String()
}
config_fields = {
    'ID': fields.Integer(),
    'MAC': fields.String(),
    'ModelPaper': fields.String(),
    'Path': fields.String(),
    'PathTag': fields.Boolean(),
    'BatchID': fields.Integer(),
    'BatchTime': fields.String(attribute=lambda x: x.BatchTime.strftime('%Y-%m-%d %H:%M:%S')),
    'Wordless': fields.Boolean(),
    'ProcessState': fields.String(),
    'YearMonth': fields.String(),
    'Warehouse': fields.String(),
    'deltag': fields.Boolean(),
    'SeletcDel': fields.Integer(),
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

class ParamConfig(Resource):

    @marshal_with(common_fields)
    def post(self):
        try:
            # 获取请求参数
            pass_tag, args = add_post_parser.parse_args() # strict=True, 不允许有额外参数
            if not pass_tag: # 参数验证不通过(名称、类型、数据结构)
                return {'msg': args}

            ID = args['ID']
            MAC = args['MAC']

            if len(MAC) != 12:
                return {'msg': "无效机器码!"}
            res = ClientBaseConfigure.query.filter_by(ID=ID).first()
            if not res: # 查不到ID
                return {'msg': "无效ID!"}
            if not res.MAC:
                return {'msg': '该ID未绑定电脑!'}
            if res.MAC != MAC: # 机器码不匹配
                return {'msg': "ID已注册!"}
            if res.ProcessState != 'Waiting': # 还有种可能, PC程序异常
                return {'msg': "参数配置失败! 原因: 系统正在上传数据, 暂无法进行参数配置!"}

            # web端可更新的参数
            ModelPaper = args['ModelPaper']
            Path = args['Path']
            PathTag = True # 每次更改配置, 默认地址有效
            YearMonth = args['YearMonth']
            Warehouse = args['Warehouse']
            deltag = args['deltag']
            SeletcDel = args['SeletcDel']
            picname = args['picname']
            
            ClientBaseConfigure.query.filter_by(ID=ID).update({ # 更新配置
                'ModelPaper': ModelPaper,
                'Path': Path,
                'PathTag': PathTag,
                'YearMonth': YearMonth,
                'Warehouse': Warehouse,
                'deltag': deltag,
                'SeletcDel': SeletcDel,
                'picname': picname,
            })
            db.session.commit()
            return {'status': 1, 'msg': "配置成功"}
        except Exception as error:
            return {'msg': str(error)}

class ClientParamConfig(Resource): # exe程序修改配置
    
    @marshal_with(common_fields)
    def post(self):
        try:
            # 获取请求参数
            pass_tag, args = add_post_parser.parse_args() # strict=True, 不允许有额外参数
            if not pass_tag: # 参数验证不通过(名称、类型、数据结构)
                return {'msg': args}

            ID = args['ID']
            MAC = args['MAC']

            if len(MAC) != 12:
                return {'msg': "无效机器码!"}
            res = ClientBaseConfigure.query.filter_by(ID=ID).first()
            if not res: # 查不到ID
                return {'msg': "无效ID!"}
            if not res.MAC:
                return {'msg': '该ID未绑定电脑!'}
            if res.MAC != MAC: # 机器码不匹配
                return {'msg': "ID已注册!"}

            # 未完成更新的参数
            PathTag = args['PathTag']
            ProcessState = args['ProcessState']
            Wordless = args['Wordless']
            picname = args['picname']

            if res.ProcessState != 'Finish':
                if not res.Wordless: # 如果已经是白纸
                    ClientBaseConfigure.query.filter_by(ID=ID).update({
                        'PathTag': PathTag,
                        'ProcessState': ProcessState,
                        'picname': picname,
                    })
                    db.session.commit()
                else: # 目前没白纸
                    ClientBaseConfigure.query.filter_by(ID=ID).update({
                        'PathTag': PathTag,
                        'ProcessState': ProcessState,
                        'Wordless': Wordless,
                        'picname': picname,
                    })
                    db.session.commit()
            else:
                res = ClientBaseConfigure.query.filter_by(ID=ID).first()
                BatchID, SeletcDel = (res.BatchID + 1), 0
                picname, ProcessState = '', 'Waiting'
                PathTag, Wordless, deltag = True, True, True
                BatchTime = datetime.datetime.now()
                ClientBaseConfigure.query.filter_by(ID=ID).update({
                    'BatchID': BatchID,
                    'SeletcDel': SeletcDel,
                    'ProcessState': ProcessState,
                    'picname': picname,
                    'PathTag': PathTag,
                    'Wordless': Wordless,
                    'deltag': deltag,
                    'BatchTime': BatchTime,
                })
                db.session.commit()
                if (res.BatchTime.strftime('%Y-%m-%d')) != BatchTime.strftime('%Y-%m-%d'):
                    ClientBaseConfigure.query.filter_by(ID=ID).update({
                        'BatchID': 1,
                    })
                    db.session.commit()
            res = ClientBaseConfigure.query.filter_by(ID=ID).first() # 查询最新信息
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
            MAC = args['MAC']

            if len(MAC) != 12: # MAC为12位16机制数
                return {'msg': "无效机器码!"}

            res = ClientBaseConfigure.query.filter_by(ID=ID).first()
            if not res: # 查不到ID
                return {'msg': "无效ID!"}
            
            if not res.MAC:
                ClientBaseConfigure.query.filter_by(ID=ID).update({'MAC': MAC}) # 绑定ID
                db.session.commit()
            else:
                if res.MAC != MAC: # 机器码不匹配
                    return {'msg': "ID已注册!"}
            return {'status': 1, 'msg': "ID注册成功!"}
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

            res = ClientBaseConfigure.query.filter_by(ID=ID).first() # ID信息查询
            if not res: # 查不到配置信息
                return {'status': 0, 'msg': "配置表中查找当前电脑的配置信息失败!"}
            if not res.MAC: # 未绑定电脑
                return {'status': 0, 'msg': "该ID未绑定电脑!"}
            return res
        except Exception as error:
            return {'status': 0, 'msg': str(error)}