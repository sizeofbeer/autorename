from apps.store.models import PicInfor, PdfInfor, db
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