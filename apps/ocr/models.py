# -*- coding:utf8  -*-
from .. import db

class PicInfor(db.Model): # 用户信息表
    # __tablename__ = "pic_infor"
    PicID = db.Column(db.Integer(), primary_key=True) # 图片编码
    IP = db.Column(db.String(255), nullable=False) # 客户端IP
    PicPath = db.Column(db.String(255), unique=True, nullable=False) # 图片路径
    ModelPaper = db.Column(db.String(255), nullable=False) # 纸质表单类型
    BatchID = db.Column(db.String(255), nullable=False) # 批次ID
    Wordless = db.Column(db.Boolean(), nullable=False, default=False) # 是否白纸, True/False
    YearMonth = db.Column(db.String(255)) # 年份-月份
    Warehouse = db.Column(db.String(255)) # 仓库
    Pdfpath = db.Column(db.String(255)) # 若为空表示未匹配完成
    Extend1 = db.Column(db.String(255))
    Extend2 = db.Column(db.String(255))
    Extend3 = db.Column(db.String(255))
    Extend4 = db.Column(db.String(255))
    Extend5 = db.Column(db.String(255))

class PdfInfor(db.Model): # 用户信息表
    # __tablename__ = "pdf_infor"
    PdfID = db.Column(db.Integer(), primary_key=True) # pdf编码
    PdfPath = db.Column(db.String(255), unique=True, nullable=False) # Pdf路径
    ModelPaper = db.Column(db.String(255), nullable=False) # 纸质表单类型
    YearMonth = db.Column(db.String(255)) # 年份-月份
    Warehouse = db.Column(db.String(255)) # 仓库
    Extend1 = db.Column(db.String(255))
    Extend2 = db.Column(db.String(255))
    Extend3 = db.Column(db.String(255))
    Extend4 = db.Column(db.String(255))
    Extend5 = db.Column(db.String(255))

