from apps.ocr.models import PicInfor, PdfInfor, PersonDeal, db
from apps.auth.models import ClientBaseConfigure
from flask_restful import Resource, fields, marshal_with
from flask import request
import datetime
from apps.ocr.utils import get_ocr_result_aip
from apps.ocr.actions import save_file
from .parsers import add_post_parser, select_post_parser, combin_post_parser

upload_fields = {
    'status': fields.Integer(default=0),
    'pic': fields.String(default=''),
    'Wordless': fields.Boolean(default=True),
    'msg': fields.String()
}
common_fields = {
    'status': fields.Integer(default=0),
    'msg': fields.String()
}

class PicUpload(Resource):
    @marshal_with(upload_fields)
    def post(self):
        try:
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

            PicID = 1 # 文件夹下第一张编号
            res = PicInfor.query.order_by(PicInfor.PicID.desc()).filter_by(ID=ID).first()
            
            if res: # 不是第一次使用
                PicID = (res.PicID) + 1
            upload_file = request.files['file'] # 图片
            print(upload_file)
            is_success, image = save_file(upload_file, MAC, PicID) # 是否保存成功
            if not is_success:
                return {'status': 0, 'msg': '图片上传失败!'}

            # 记录图片信息
            PicPath = image
            BatchID = args['BatchID']
            WarehouseCode = args['WarehouseCode']
            ModelPaperCode = args['ModelPaperCode']

            BatchTime = datetime.datetime.strptime(args['BatchTime'], "%Y-%m-%d %H:%M:%S")
            # 需要使用OCR来判断, 目前先不做
            result = get_ocr_result_aip(image)['result']
            Wordless, deltag = True, True
            if len(result) <= 15:
                Wordless = False
                deltag = False
            YearMonth = args['YearMonth']
            # 创建图片信息对象, 添加到数据库
            obj = PicInfor(
                PicID=PicID,
                PicPath=PicPath,
                ID=ID,
                MAC=MAC,
                ModelPaperCode=ModelPaperCode,
                BatchID=BatchID,
                BatchTime=BatchTime,
                Wordless=Wordless,
                YearMonth=YearMonth,
                WarehouseCode=WarehouseCode,
            )
            db.session.add(obj)
            db.session.commit()
            ClientBaseConfigure.query.filter_by(ID=ID).update({'Wordless': Wordless, 'deltag': deltag})
            db.session.commit()
            return {'status': 1, 'Wordless': Wordless, 'pic': str(PicID), 'msg': '图片上传成功!'}
        except Exception as error:
            return {'status': 0, 'msg': str(error)}

import base64
class StartHandSelectUpload(Resource):
    
    def post(self):
        returnData = {
            'data': [],
            'msg': '',
            'status': 0
        }
        # if True:
        try:
            pass_tag, args = select_post_parser.parse_args() # strict=True, 不允许有额外参数
            if not pass_tag: # 参数验证不通过(名称、类型、数据结构)
                returnData['msg'] = args
                return returnData
           
            ID = args['ID']
            # number = args['number']
            ModelPaperCode = args['ModelPaperCode']

            res = PersonDeal.query.filter_by(ID=ID, ModelPaperCode=ModelPaperCode).first()
            info = PicInfor.query.filter(PicInfor.Pdfpath==None).first()
            if not info:
                returnData['status'] = 1
                returnData['msg'] = "已全部处理!"
                return returnData
            if not res: # 初始化 PicnameTag, 以第一个pdfpath为空的作为起点
                hand = PersonDeal(ID=ID, ModelPaperCode=ModelPaperCode, PicnameTag=str(info.PicID))
                db.session.add(hand)
                db.session.commit()
            else: # 查找pdfpath为空的图片
                PersonDeal.query.filter_by(ID=ID, ModelPaperCode=ModelPaperCode).update({"PicnameTag": str(info.PicID)})
                db.session.commit()
            # 查询最新
            res = PersonDeal.query.filter_by(ID=ID, ModelPaperCode=ModelPaperCode).first()
            PicnameTag = int(res.PicnameTag) # 位置、图片编号
            # PicnameTag = 5 # 测试
            showID = 1
            if PicnameTag <= 4:
                res_list = PicInfor.query.filter_by(ID=ID, ModelPaperCode=ModelPaperCode).limit(9).all() # 查询前九条
                if not res_list:
                    returnData['msg'] = '数据库无数据'
                    return returnData
                for res in res_list:
                    show_fields = {
                        'showID': showID,
                        'PicID': res.PicID,
                        'ID': res.ID,
                        'MAC': res.MAC,
                        'PicPath': res.PicPath,
                        'ModelPaperCode': res.ModelPaperCode,
                        'BatchID': res.BatchID,
                        'BatchTime': res.BatchTime.strftime('%Y-%m-%d %H:%M:%S'),
                        'Wordless': res.Wordless,
                        'YearMonth': res.YearMonth,
                        'WarehouseCode': res.WarehouseCode,
                        'Pdfpath': res.Pdfpath,
                        'pic': ''
                    }
                    showID += 1
                    with open(res.PicPath, 'rb') as f:
                        show_fields['pic'] = str(base64.b64encode(f.read())) # base编码
                    returnData['data'].append(show_fields)
            else:
                for i in range(PicnameTag - 3, PicnameTag + 6):
                    res = PicInfor.query.get(i)
                    if not res:
                        returnData['msg'] = '本次查询为图片不足9张!'
                        break
                    show_fields = {
                        'showID': showID,
                        'PicID': res.PicID,
                        'ID': res.ID,
                        'MAC': res.MAC,
                        'PicPath': res.PicPath,
                        'ModelPaperCode': res.ModelPaperCode,
                        'BatchID': res.BatchID,
                        'BatchTime': res.BatchTime.strftime('%Y-%m-%d %H:%M:%S'),
                        'Wordless': res.Wordless,
                        'YearMonth': res.YearMonth,
                        'WarehouseCode': res.WarehouseCode,
                        'Pdfpath': res.Pdfpath,
                        'pic': ''
                    }
                    showID += 1
                    with open(res.PicPath, 'rb') as f:
                        show_fields['pic'] =str(base64.b64encode(f.read())) # base编码
                    returnData['data'].append(show_fields)
            print(returnData['data'])
            returnData['msg'] = '获取图片成功!'
            returnData['status'] = 1
            return returnData
        except Exception as error:
            return returnData

class CombinHandSelectPic(Resource):

    @marshal_with(common_fields)
    def post(self):
        try:
            pass_tag, args = combin_post_parser.parse_args() # strict=True, 不允许有额外参数
            if not pass_tag: # 参数验证不通过(名称、类型、数据结构)
                return {'status': 0, 'msg': args}
            
            data = args['data'] # 小于等于9
            if len(data) > 9:
                return {'status': 0, 'msg': '合并数据个数大于9!'}
            PicID_series = 0
            for row in data:
                if PicID_series == 0:
                    PicID_series = int(row['PicID'])
                else:
                    if abs(PicID_series - int(row['PicID'])) != 1: # 不连续
                        return {'status': 0, 'msg': "点选图片不连续, 请重新点选!"}
                res = PicInfor.query.get(PicID_series) # 获取该图片的首位
                PicInfor.query.filter_by(ID=int(row['ID']), PicID=int(row['PicID'])).update(
                    {
                        'ModelPaperCode': row['ModelPaperCode'],
                        'BatchID': int(row['BatchID']),
                        'BatchTime': row['BatchTime'],
                        'YearMonth': row['YearMonth'],
                        'WarehouseCode': row['WarehouseCode'],
                        'Pdfpath': row['Pdfpath'],
                    }
                )
                db.session.commit()
            return {'status': 1, 'msg': "合并成功!"}
        except Exception as error:
            return {'status': 0, 'msg': str(error)}
# # -*- coding:utf8  -*-
# from flask_restful import Resource
# from flask import request
# import os, uuid
# from ..ocr.models import *

# ''' 一些OCR 功能 '''
# from apps.ocr.ocr_app import get_hilti_value
# class Hilti_Upload(Resource):
#     def post(self):
#         returnData = {
#             'status': 0,
#             "result": '',
#             "msg": ''
#         }
#         image_id = uuid.uuid4()
#         image_path = os.path.join(tmp_path, "{}.jpg".format(image_id))
#         try:
#             f = request.files['file']
#             if not f:
#                 returnData['msg'] = "文件未上传"
#                 return returnData
#             f.save(image_path)
#         except Exception:
#             returnData['msg'] = "文件上传失败"
#             return returnData
#         result_line_value, areas_box, excel_colume = get_hilti_value(image_path)
#         result = result_line_value[0]
#         if result == "":
#             returnData['msg'] = "OCR识别失败"
#             return returnData
#         returnData['msg'] = "OCR识别成功"
#         returnData['status'] = 1
#         db_ocr = Ocr_Hilti()
#         task = db_ocr.query.filter_by(ocrresult = result).first()
#         if not task:
#             insert_data = []
#             insert_data.append([result, "1"])
#             db.session.execute(db_ocr.__table__.insert(),
#                 [{
#                     "ocrresult": data[0], "ocrcount": data[1]
#                 } for data in insert_data]
#             )
#             db.session.commit()
#             returnData['result'] = result + "-1"
#             return returnData
#         new_count = str(int(task.ocrcount) + 1)
#         update_data = []
#         update_data.append([result, new_count])
#         keys = ["ocrresult", "ocrcount"]
#         for ele in update_data:
#             filters = {}
#             for i in range(len(keys)):
#                 filters[keys[i]] = ele[i]
#             res = db_ocr.query.filter_by(ocrresult = ele[0]).update(filters)
#             db.session.commit()
#         returnData['result'] = result + "-" + new_count
#         return returnData
# from apps.ocr.ocr_app import get_warehouse_value
# class Warehouse_Ocr_Rename(Resource):
#     def post(self):
#         returnData = {
#             'status': 0,
#             "result": [],
#             "msg": ''
#         }
#         image_id = uuid.uuid4()
#         image_path = os.path.join(tmp_path, "{}.jpg".format(image_id))
#         try:
#             f = request.files['file']
#             if not f:
#                 returnData['msg'] = "文件未上传"
#                 return returnData
#             f.save(image_path)
#         except Exception:
#             returnData['msg'] = "文件上传失败"
#             return returnData
#         result_line_value, areas_box, excel_colume = get_warehouse_value(image_path)
#         print(result_line_value)
#         if not result_line_value:
#             returnData['msg'] = "OCR识别失败"
#             return returnData
#         returnData['msg'] = "OCR识别成功"
#         returnData['status'] = 1
#         returnData['result'] = result_line_value
#         return returnData
