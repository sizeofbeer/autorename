# -*- coding:utf8  -*-
from .. import db

class WarehouseInfor(db.Model): # 仓库信息表
    # __tablename__ = "warehouse_infor"
    WarehouseCode = db.Column(db.String(255), primary_key=True)
    Warehouse = db.Column(db.String(255), nullable=False) # 仓库
    Extend1 = db.Column(db.String(255))
    Extend2 = db.Column(db.String(255))
    Extend3 = db.Column(db.String(255))
    Extend4 = db.Column(db.String(255))
    Extend5 = db.Column(db.String(255))

class ModelInfor(db.Model): # 模型信息表
    # __tablename__ = "model_infor"
    ModelCode = db.Column(db.String(255), primary_key=True) # 仓库
    Model = db.Column(db.String(255), nullable=False) # 仓库
    Extend1 = db.Column(db.String(255))
    Extend2 = db.Column(db.String(255))
    Extend3 = db.Column(db.String(255))
    Extend4 = db.Column(db.String(255))
    Extend5 = db.Column(db.String(255))