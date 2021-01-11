import uuid, os
from ..auth.models import UserInfor
from os.path import dirname, abspath

path = dirname(abspath(__file__))
tmp_path = os.path.join(path, 'tmp')
if not os.path.exists(tmp_path):os.mkdir(tmp_path)


def save_file(upload_file):
    file_id = uuid.uuid4()
    new_file = os.path.join(tmp_path, "{}.jpg".format(file_id))
    if (not upload_file) or (upload_file is None):
        return False, new_file
    upload_file.save(new_file)
    return True, new_file

# 根据token区分功能
def split_by_token(token):
    user = UserInfor.verify_auth_token(token) # 验证token
    if not user: # 验证不通过
        return False
    return user.Role # 返回用户权限
