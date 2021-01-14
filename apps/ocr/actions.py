from os.path import dirname, abspath
import os

path = dirname(abspath(__file__))
tmp_path = os.path.join(path, 'tmp')
if not os.path.exists(tmp_path):os.mkdir(tmp_path)


def save_file(upload_file, MAC, PicID):
    if (not upload_file) or (upload_file is None):
        return False, new_file
    out_path = os.path.join(tmp_path, MAC)
    if not os.path.exists(out_path):os.mkdir(out_path)
    new_file = os.path.join(out_path, "{}.jpg".format(str(PicID)))
    upload_file.save(new_file)
    return True, new_file