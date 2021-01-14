from apps.ocr.models import PicInfor, PdfInfor, db
from apps.auth.models import ClientBaseConfigure
from flask_restful import Resource, fields, marshal_with
from flask import request
import datetime
from apps.ocr.actions import save_file
from .parsers import add_post_parser

upload_fields = {
    'status': fields.Integer(default=0),
    'pic': fields.String(default=''),
    'Wordless': fields.Boolean(default=True),
    'msg': fields.String()
}

class PicUpload(Resource):
    @marshal_with(upload_fields)
    def post(self):
        try:
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
            
            PicID = 1 # 文件夹下第一张编号
            res = PicInfor.query.order_by(PicInfor.PicID.desc()).filter_by(ID=ID, MAC=MAC).first()
            
            if res: # 不是第一次使用
                PicID = (res.PicID) + 1

            upload_file = request.files['file'] # 图片
            is_success, image = save_file(upload_file, MAC, PicID) # 是否保存成功
            if not is_success:
                return {'msg': '图片上传失败!'}

            # 记录图片信息
            PicPath = image
            ModelPaper = args['ModelPaper']
            BatchID = args['BatchID']
            BatchTime = datetime.datetime.strptime(args['BatchTime'], "%Y-%m-%d %H:%M:%S")
            ''' 需要使用OCR来判断, 目前先不做 '''
            Wordless = True
            YearMonth = args['BatchTime']
            Warehouse = args['Warehouse']
            # 创建图片信息对象, 添加到数据库
            obj = PicInfor(
                PicID=PicID,
                PicPath=PicPath,
                ID=ID,
                MAC=MAC,
                ModelPaper=ModelPaper,
                BatchID=BatchID,
                BatchTime=BatchTime,
                Wordless=Wordless,
                YearMonth=YearMonth,
                Warehouse=Warehouse,
            )
            db.session.add(obj)
            db.session.commit()

            return {'status': 1, 'Wordless': Wordless, 'pic': str(PicID), 'msg': '图片上传成功!'}
        except Exception as error:
            return {'msg': str(error)}




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
