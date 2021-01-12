from .. import db

class WarehouseInfor(db.Model): # 仓库信息表
    # __tablename__ = "warehouse_infor"
    Warehouse = db.Column(db.String(255), primary_key=True) # 仓库
    Extend1 = db.Column(db.String(255))
    Extend2 = db.Column(db.String(255))
    Extend3 = db.Column(db.String(255))
    Extend4 = db.Column(db.String(255))
    Extend5 = db.Column(db.String(255))

class ModelInfor(db.Model): # 模型信息表
    # __tablename__ = "model_infor"
    Model = db.Column(db.String(255), primary_key=True) # 仓库
    Extend1 = db.Column(db.String(255))
    Extend2 = db.Column(db.String(255))
    Extend3 = db.Column(db.String(255))
    Extend4 = db.Column(db.String(255))
    Extend5 = db.Column(db.String(255))

class ClientBaseConfigure(db.Model): # 纸质表单配置信息表
    # __tablename__ = "client_base_configure"
    index = db.Column(db.Integer(), primary_key=True, autoincrement=True) # 计数用
    ID = db.Column(db.Integer(), nullable=False) # 客户端授权码
    ModelPaper = db.Column(db.String(255), nullable=False) # 纸质表单类型
    Path = db.Column(db.String(255), nullable=False) # 扫描仪存储路径
    PathTag = db.Column(db.Boolean(), nullable=False, default=True) # 扫描仪扫描件存储路径是否存在
    YearMonth = db.Column(db.String(255), nullable=False) # 年份-月份
    Warehouse = db.Column(db.String(255), nullable=False) # 仓库
    BatchID = db.Column(db.String(255), nullable=False) # 批次ID
    deltag = db.Column(db.Boolean(), nullable=False, default=True) # 删除标记
    Wordless = db.Column(db.Boolean(), nullable=False, default=True) # 是否白纸, True/False
    ProcessState = db.Column(db.String(255), nullable=False, default="Waiting") # 进程状态, Waiting/doing/finish
    picname = db.Column(db.String(255), nullable=False, default="") # 若当前图片能读取,该项为空; 否则为图片名称
    Extend1 = db.Column(db.String(255))
    Extend2 = db.Column(db.String(255))
    Extend3 = db.Column(db.String(255))
    Extend4 = db.Column(db.String(255))
    Extend5 = db.Column(db.String(255))