from flask_restful import Resource, fields, marshal_with
from apps.auth.models import UserInfor, ClientBaseConfigure, db
from apps.auth.permission import AuthResource

user_fields = {
    'ID': fields.Integer(),
    'Name': fields.String(),
    'Password': fields.String(),
    'Role': fields.String()
}
common_fields = {
    'status': fields.Integer(default=0),
    'msg': fields.String()
}

from .parsers import (
    login_post_parser,
    search_post_parser, # 查询/删除
    add_post_parser, # 添加/更新
)

# 用户登录
class Login(AuthResource):
    returnData = {
        'status': fields.Integer(default=0),
        'Name': fields.String(),
        'Role': fields.String(),
        'token': fields.String(),
        'msg': fields.String()
    }

    @marshal_with(returnData)
    def post(self):
        try:
            # 获取请求参数
            pass_tag, args = login_post_parser.parse_args() # strict=True, 不允许有额外参数
            if not pass_tag: # 参数验证不通过(名称、类型、数据结构)
                return {'msg': args}

            Name = args['Name']
            Password = args['Password']

            res = UserInfor.query.filter_by(Name=Name, Password=Password).first() # 查询是否通过
            if not res:
                return {'msg': "请检查用户名和密码!"}

            token = res.generate_auth_token(7200) # 创建token
            token = str(token, encoding="utf8")

            return {'token': token, 'Name': Name, 'Role': res.Role, 'msg': "用户登录成功!", 'status': 1}
        except Exception as error:
            return {'msg': str(error)}

# 用户查询
class UserSearch(AuthResource):
    returnData = {
        'status': fields.Integer(default=0),
        'columns': fields.List(fields.Nested(user_fields)),
        'msg': fields.String()
    }

    @marshal_with(returnData)
    def post(self):
        try:
            pass_tag, args = search_post_parser.parse_args() # strict=True, 不允许有额外参数
            if not pass_tag:
                return {'msg': args}

            Name = args['Name']

            if Name: # 不为空
                # 模糊查询该用户信息
                res_list = UserInfor.query.filter(UserInfor.Name.like('%{Name}%'.format(Name=Name))).all()
                if not res_list: # 查询不到
                    return {'msg': "该用户不存在!"}
                return {'msg': "用户查询成功!", 'status': 1, 'columns': res_list}
            else:
                res_list = UserInfor.query.all() # 获取所有用户信息
                if not res_list: # 查询不到
                    return {'msg': "数据库无数据!"}
                return {'msg': "用户查询成功!", 'status': 1, 'columns': res_list}
        except Exception as error:
            return {'msg': str(error)}

# 用户添加
class UserAdd(AuthResource):
    @marshal_with(common_fields)
    def post(self):
        try:
            pass_tag, args = add_post_parser.parse_args() # strict=True, 不允许有额外参数
            if not pass_tag:
                return {'msg': args}

            Name = args['Name']
            Password = args['Password']
            Role = args['Role']

            if Role not in ['superAdmin', 'Admin', 'user']: # 角色类型检测
                return {'msg': "非法角色类型!"}

            if UserInfor.query.filter_by(Name=Name).first(): # 如果该姓名已存在
                return {'msg': "用户名已存在, 新增用户失败!"}

            user = UserInfor( # 创建用户对象
                Name=Name,
                Password=Password,
                Role=Role,
            )
            config = ClientBaseConfigure() # 创建配置
            user.Config = config # 绑定授权码
            db.session.add(user) # 添加到数据库
            db.session.commit() # 提交
            return {'status': 1, 'msg': "用户添加成功!"}
        except Exception as error:
            return {'msg': str(error)}

# 用户更新
class UserUpdate(AuthResource):
    @marshal_with(common_fields)
    def post(self):
        try:
            pass_tag, args = add_post_parser.parse_args() # strict=True, 不允许有额外参数
            if not pass_tag:
                return {'msg': args}

            Name = args['Name']
            Password = args['Password']
            Role = args['Role']
            
            if Role not in ['superAdmin', 'Admin', 'user']: # 角色类型检测
                return {'msg': "非法角色类型!"}

            res = UserInfor.query.filter_by(Name=Name).first()
            if not res: # 如果该姓名不存在
                return {'msg': "该用户不存在!"}

            UserInfor.query.filter_by(Name=Name).update({'Password': Password, 'Role': Role}) # 更新数据
            db.session.commit() # 提交
            return {'status': 1, 'msg': "用户更新成功!"}
        except Exception as error:
            return {'msg': str(error)}

# 用户删除
class UserDel(AuthResource):
    @marshal_with(common_fields)
    def post(self):
        try:
            pass_tag, args = search_post_parser.parse_args() # strict=True, 不允许有额外参数
            if not pass_tag:
                return {'msg': args}

            Name = args['Name']

            res = UserInfor.query.filter_by(Name=Name).first() # 查询该用户信息
            if not res: # 查询不到
                return {'msg': "该用户不存在!"}
            
            db.session.delete(res)
            db.session.commit()

            return {'status': 1, 'msg': "用户删除成功!"}
        except Exception as error:
            return {'msg': str(error)}