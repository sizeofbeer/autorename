from flask_restful import Resource, fields, marshal_with
import datetime, os
from .parsers import search_post_parser, add_post_parser, author_post_parser
from apps.store.models import ModelInfor, WarehouseInfor, db
from apps.auth.models import ClientBaseConfigure
from apps.ocr.models import PicInfor

def datetime2str(x):
    try:
        s = x.BatchTime.strftime('%Y-%m-%d %H:%M:%S')
    except:
        return None
    return s

config_fields = {
    'ID': fields.Integer(),
    'MAC': fields.String(),
    'ModelPaperCode': fields.String(),
    'Path': fields.String(),
    'PathTag': fields.Boolean(),
    'BatchID': fields.Integer(),
    'BatchTime': fields.String(attribute=lambda x:  datetime2str(x)),
    'Wordless': fields.Boolean(),
    'ProcessState': fields.String(),
    'YearMonth': fields.String(),
    'WarehouseCode': fields.String(),
    'deltag': fields.Boolean(),
    'SeletcDel': fields.Integer(),
    'picname': fields.String(),
    'status': fields.Integer(default=1),
    'msg': fields.String(default='状态配置/查询成功!')
}

common_fields = {
    'status': fields.Integer(default=0),
    'msg': fields.String()
}

class ModelSelect(Resource):
    Model_fields = {
        'ModelCode': fields.String(),
        'Model': fields.String()
    }
    returnData = {
        'status': fields.Integer(default=0),
        'Model': fields.List(fields.Nested(Model_fields)),
        'msg': fields.String()
    }

    @marshal_with(returnData)
    def post(self):
        try:
            res_list = ModelInfor.query.all() # 获取所有模板信息

            if not res_list:
                return {'msg': "暂无模板信息!"}

            return {'status': 1, 'msg': "模型获取成功!", 'Model': res_list}
        except Exception as error:
            return {'msg': str(error)}

class WarehouseSelect(Resource):
    Warehouse_fields = {
        'WarehouseCode': fields.String(),
        'Warehouse': fields.String()
    }
    returnData = {
        'status': fields.Integer(default=0),
        'Warehouse': fields.List(fields.Nested(Warehouse_fields)),
        'msg': fields.String()
    }

    @marshal_with(returnData)
    def post(self):
        try:
            res_list = WarehouseInfor.query.all() # 获取所有仓库信息
            if not res_list:
                return {'msg': "暂无仓库信息!"}

            return {'status': 1, 'msg': "模型获取成功!", 'Warehouse': res_list}
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
                return {'status': 0, 'msg': args}

            ID = args['ID']
            MAC = args['MAC']

            if len(MAC) != 12:
                return {'status': 0, 'msg': "无效机器码!"}
            res = ClientBaseConfigure.query.filter_by(ID=ID).first()
            if not res: # 查不到ID
                return {'status': 0, 'msg': "无效ID!"}
            if not res.MAC:
                return {'status': 0, 'msg': '该ID未绑定电脑!'}
            if res.MAC != MAC: # 机器码不匹配
                return {'status': 0, 'msg': "ID已注册!"}
            
            SeletcDel = args['SeletcDel']
            if res.ProcessState != 'Waiting': # 还有种可能, PC程序异常
                if SeletcDel == 0: # 人工确认白纸
                    return {'status': 0, 'msg': "参数配置失败! 原因: 系统正在上传数据, 暂无法进行参数配置!"}

            # web端可更新的参数
            ModelPaperCode = args['ModelPaperCode']
            Path = args['Path']
            PathTag = True # 每次更改配置, 默认地址有效
            YearMonth = args['YearMonth']
            WarehouseCode = args['WarehouseCode']
    
            ClientBaseConfigure.query.filter_by(ID=ID).update({ # 更新配置
                'ModelPaperCode': ModelPaperCode,
                'Path': Path,
                'PathTag': PathTag,
                'YearMonth': YearMonth,
                'WarehouseCode': WarehouseCode,
                'SeletcDel': SeletcDel,
            })
            db.session.commit()
            return {'status': 1, 'msg': "配置成功"}
        except Exception as error:
            return {'status': 0, 'msg': str(error)}

class ClientParamConfig(Resource): # exe程序修改配置

    @marshal_with(common_fields)
    def post(self):
        try:
            # 获取请求参数
            pass_tag, args = add_post_parser.parse_args() # strict=True, 不允许有额外参数
            if not pass_tag: # 参数验证不通过(名称、类型、数据结构)
                return {'status': 0, 'msg': args}

            ID = args['ID']
            MAC = args['MAC']

            if len(MAC) != 12:
                return {'status': 0, 'msg': "无效机器码!"}
            res = ClientBaseConfigure.query.filter_by(ID=ID).first()
            if not res: # 查不到ID
                return {'status': 0, 'msg': "无效ID!"}
            if not res.MAC:
                return {'status': 0, 'msg': '该ID未绑定电脑!'}
            if res.MAC != MAC: # 机器码不匹配
                return {'status': 0, 'msg': "ID已注册!"}
            print(res.Wordless, res.deltag)
            # 后期可以并行Task
            if not res.deltag: # 删除文件及数据库
                del_list = PicInfor.query.filter_by(ID=ID, MAC=MAC, BatchID=res.BatchID, BatchTime=res.BatchTime).all()
                for del_file in del_list:
                    os.remove(del_file.PicPath)
                    db.session.delete(del_file)
                    db.session.commit()

            # if not res.Wordless: # 存在白纸
            #     return {'status': 0, 'msg': "当前批次存在白纸!"}

            # 未完成更新的参数
            PathTag = args['PathTag']
            ProcessState = args['ProcessState']
            # Wordless = args['Wordless']
            picname = args['picname']
            BatchTime = datetime.datetime.now()

            if res.ProcessState == 'Waiting' and (res.BatchTime.strftime('%Y-%m-%d')) != BatchTime.strftime('%Y-%m-%d'):
                ClientBaseConfigure.query.filter_by(ID=ID).update({
                    'BatchID': 1,
                    'BatchTime': BatchTime
                })
                db.session.commit()
            if res.ProcessState == 'Waiting' and ProcessState == 'Doing':
                ClientBaseConfigure.query.filter_by(ID=ID).update({
                    'BatchTime': BatchTime
                })
                db.session.commit()
            if res.ProcessState != 'Finish':
                ClientBaseConfigure.query.filter_by(ID=ID).update({
                    'PathTag': PathTag,
                    'ProcessState': ProcessState,
                    'picname': picname,
                })
                db.session.commit()
            else:
                res = ClientBaseConfigure.query.filter_by(ID=ID).first()
                if (not res.Wordless) and (res.SeletcDel == 0):
                    return {'status': 0, 'msg': "请确认是否进行下一批次!"}
                # 下一批次
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
            return {'status': 1, 'msg': "配置成功"}
        except Exception as error:
            return {'status': 0, 'msg': str(error)}

class AuthorConfig(Resource):
    
    @marshal_with(common_fields)
    def post(self):
        try:
            pass_tag, args = author_post_parser.parse_args() # strict=True, 不允许有额外参数
            if not pass_tag: # 参数验证不通过(名称、类型、数据结构)
                return {'status': 0, 'msg': args}

            ID = args['ID']
            MAC = args['MAC']
            print(ID, MAC)

            if len(MAC) != 12: # MAC为12位16机制数
                return {'status': 0, 'msg': "无效机器码!"}

            res = ClientBaseConfigure.query.filter_by(ID=ID).first()
            if not res: # 查不到ID
                return {'status': 0, 'msg': "无效ID!"}
            
            if not res.MAC:
                ClientBaseConfigure.query.filter_by(ID=ID).update({'MAC': MAC}) # 绑定ID
                db.session.commit()
            else:
                if res.MAC != MAC: # 机器码不匹配
                    return {'status': 0, 'msg': "ID已注册!"}
            return {'status': 1, 'msg': "ID注册成功!"}
        except Exception as error:
            return {'status': 0, 'msg': str(error)}

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
                return {'ID': ID, 'status': 0, 'msg': "配置表中查找当前电脑的配置信息失败!"}
            if not res.MAC: # 未绑定电脑
                return {'ID': ID, 'status': 0, 'msg': "该ID未绑定电脑!"}
            if not res.PathTag:
                print('当前路径不存在!')
                config_fields['status'] = fields.Integer(default=0)
                config_fields['msg'] = fields.String(default='当前路径不存在!')
                return res
            if not res.Wordless:
                config_fields['status'] = fields.Integer(default=1)
                config_fields['msg'] = fields.String(default='当前批次存在白纸!')
                return res
            config_fields['status'] = fields.Integer(default=1)
            config_fields['msg'] = fields.String(default='查询成功!')
            return res
        except Exception as error:
            return {'ID': ID, 'status': 0, 'msg': str(error)}

