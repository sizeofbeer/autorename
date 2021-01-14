from .. import db, app
import time, jwt, datetime

class UserInfor(db.Model): # 用户信息表
    # __tablename__ = "user_infor"
    ID = db.Column(db.Integer(), primary_key=True, autoincrement=True) # 机器编号(自增)
    Name = db.Column(db.String(255), primary_key=True) # 用户名
    # 注释部分扩展性更好
    # Name = db.Column(db.String(255), primary_key=True) # 用户名
    # ID = db.Column(db.Integer(), unique=True, nullable=False) # 机器编号(自增)
    Password = db.Column(db.String(255), nullable=False) # 密码
    Role = db.Column(db.String(255), nullable=False) # 角色, superAdmin/Admin/user
    Config = db.relationship("ClientBaseConfigure", backref="user_infor", uselist=False)
    Extend1 = db.Column(db.String(255))
    Extend2 = db.Column(db.String(255))
    Extend3 = db.Column(db.String(255))
    Extend4 = db.Column(db.String(255))
    Extend5 = db.Column(db.String(255))
    def generate_auth_token(self, expires_in=600):
        return jwt.encode(
            {'Name': self.Name, 'exp': time.time() + expires_in},
            app.config.get('SECRET_KEY'), algorithm='HS256')

    @staticmethod
    def verify_auth_token(token):
        try:
            data = jwt.decode(
                token,
                app.config.get('SECRET_KEY'),
                algorithms=['HS256'],
            )
        except:
            return None
        return UserInfor.query.filter_by(Name = data['Name']).first()

class ClientBaseConfigure(db.Model): # 纸质表单配置信息表
    # __tablename__ = "client_base_configure"
    ID = db.Column(db.Integer(), db.ForeignKey('user_infor.ID'), primary_key=True) # 客户端授权码
    MAC = db.Column(db.String(12), nullable=False, default="") # 机器码
    ModelPaper = db.Column(db.String(255), nullable=False, default="") # 纸质表单类型
    Path = db.Column(db.String(255), nullable=False, default="") # 扫描仪存储路径
    PathTag = db.Column(db.Boolean(), nullable=False, default=True) # 扫描仪扫描件存储路径是否存在
    BatchID = db.Column(db.Integer(), nullable=False, default=1) # 批次ID
    BatchTime = db.Column(db.DateTime(), nullable=False, default=datetime.datetime.now) # 批次时间
    Wordless = db.Column(db.Boolean(), nullable=False, default=True) # 是否白纸, True/False
    ProcessState = db.Column(db.String(255), nullable=False, default="Waiting") # 进程状态, Waiting/doing/finish
    YearMonth = db.Column(db.String(255), nullable=False, default="") # 年份-月份
    Warehouse = db.Column(db.String(255), nullable=False, default="") # 仓库
    deltag = db.Column(db.Boolean(), nullable=False, default=True) # 删除标记
    SeletcDel = db.Column(db.Integer(), nullable=False, default=0)
    picname = db.Column(db.String(255), nullable=False, default="") # 若当前图片能读取,该项为空; 否则为图片名称
    Extend1 = db.Column(db.String(255))
    Extend2 = db.Column(db.String(255))
    Extend3 = db.Column(db.String(255))
    Extend4 = db.Column(db.String(255))
    Extend5 = db.Column(db.String(255))