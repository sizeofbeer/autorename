import os
from ..auth.models import UserInfor
from os.path import dirname, abspath

path = dirname(abspath(__file__))
tmp_path = os.path.join(path, 'tmp')
if not os.path.exists(tmp_path):os.mkdir(tmp_path)


def save_file(upload_file, BatchID):
    if (not upload_file) or (upload_file is None):
        return False, new_file
    
    out_path = os.path.join(tmp_path, BatchID)
    if not os.path.exists(out_path):os.mkdir(out_path)

    name = (str(upload_file.name)).split('.')[0]
    new_file = os.path.join(out_path, "{}.jpg".format(name))
    upload_file.save(new_file)
    return True, new_file

# 根据token区分功能
def split_by_token(token):
    user = UserInfor.verify_auth_token(token) # 验证token
    if not user: # 验证不通过
        return False
    return user.Role # 返回用户权限
