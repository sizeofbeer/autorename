from .. import db, app
import time, jwt

class UserInfor(db.Model): # 用户信息表
    # __tablename__ = "user_infor"
    ID = db.Column(db.Integer(), primary_key=True, autoincrement=True) # 人员编号(自增)
    Name = db.Column(db.String(255), unique=True, nullable=False) # 用户名
    Password = db.Column(db.String(255), nullable=False) # 密码
    Role = db.Column(db.String(255), nullable=False, default="user") # 角色, superAdmin/Admin/user
    authorKeys = db.relationship(
        'AuthorKey', # 关联类
        backref='user_infor', # 反向引用指定表
        lazy='dynamic' # 控制加载相关对象
    )
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

class AuthorKey(db.Model): # 授权码
    # __tablename__ = "author_key"
    ID = db.Column(db.Integer(), primary_key=True, autoincrement=True) # 授权码(自增)
    machineCode = db.Column(db.String(255)) # 机器码
    user_id = db.Column(db.Integer(), db.ForeignKey('user_infor.ID')) # 外键
    Extend1 = db.Column(db.String(255))
    Extend2 = db.Column(db.String(255))
    Extend3 = db.Column(db.String(255))
    Extend4 = db.Column(db.String(255))
    Extend5 = db.Column(db.String(255))

