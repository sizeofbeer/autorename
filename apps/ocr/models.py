# -*- coding:utf8  -*-
from .. import db

class PicInfor(db.Model): # 用户信息表
    # __tablename__ = "pic_infor"
    PicID = db.Column(db.Integer(), primary_key=True) # 图片编码
    PicPath = db.Column(db.String(255)) # 图片路径
    ID = db.Column(db.Integer()) # 客户端ID
    MAC = db.Column(db.String(255))
    ModelPaperCode = db.Column(db.String(255), nullable=False) # 纸质表单类型
    BatchID = db.Column(db.Integer(), nullable=False) # 批次ID
    BatchTime = db.Column(db.DateTime(), nullable=False) # 批次时间
    Wordless = db.Column(db.Boolean()) # 是否白纸, True/False
    YearMonth = db.Column(db.String(255)) # 年份-月份
    WarehouseCode = db.Column(db.String(255)) # 仓库
    Pdfpath = db.Column(db.String(255)) # 若为空表示未匹配完成
    Extend1 = db.Column(db.String(255))
    Extend2 = db.Column(db.String(255))
    Extend3 = db.Column(db.String(255))
    Extend4 = db.Column(db.String(255))
    Extend5 = db.Column(db.String(255))

class PdfInfor(db.Model): # 用户信息表
    # __tablename__ = "pdf_infor"
    PdfID = db.Column(db.Integer(), primary_key=True) # pdf编码
    PdfPath = db.Column(db.String(255), primary_key=True) # Pdf路径
    ModelPaperCode = db.Column(db.String(255), nullable=False) # 纸质表单类型
    YearMonth = db.Column(db.String(255)) # 年份-月份
    WarehouseCode = db.Column(db.String(255)) # 仓库
    Extend1 = db.Column(db.String(255))
    Extend2 = db.Column(db.String(255))
    Extend3 = db.Column(db.String(255))
    Extend4 = db.Column(db.String(255))
    Extend5 = db.Column(db.String(255))

class PersonDeal(db.Model): # 人工处理标志描述表
    # __tablename__ = "person_deal"
    ID = db.Column(db.Integer(), primary_key=True) # 客户端ID
    ModelPaperCode = db.Column(db.String(255), primary_key=True) # 纸质表单类型
    PicnameTag = db.Column(db.String(255), nullable=False)