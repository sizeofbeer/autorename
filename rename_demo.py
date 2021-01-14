import requests, json, time, uuid, os, glob, mimetypes
from os.path import dirname, abspath

path = dirname(abspath(__file__))
config_file = os.path.join(path, 'init.json')
if not os.path.exists(config_file): # 文件不存在
    with open(config_file, "w") as f:
        json.dump({'ID': 0}, f)

# 参数初始化
ID, BatchID, SeletcDel = 0, 0, 0 # 从配置文件读取, 批次ID一定不为-1
MAC = (uuid.uuid1().hex)[-12:].upper() # 本机mac码
ModelPaper, Path, BatchTime, YearMonth, Warehouse, picname = '', '', '', '', '', ''
PathTag, Wordless, ProcessState, deltag = True, True, True, True

web = 'http://cmsoftware.mynatapp.cc/EPD/'
author_url = web + 'AuthorConfig' # 用于授权码注册
search_url = web + 'PrintAndUpStatusSearch' # 查询配置信息
config_url = web + 'ClientParamConfig' # 修改配置信息
upload_url = web + 'PicUpload' # 上传图片
headers = {'content-type':'application/x-www-form-urlencoded'}

author_params = {'ID': ID, 'MAC': MAC} # 用在 author_url和 upload_url
search_params = {'ID': ID}
config_params = {
    'ID': ID, # 授权码
    'MAC': MAC,
    'ModelPaper': ModelPaper, # 模板
    'Path': Path, # 路径
    'PathTag': PathTag, # 路径是否有效
    'BatchID': BatchID, # 批次号
    'BatchTime': BatchTime, # 批次时间
    'Wordless': Wordless, # 是否有字
    'ProcessState': ProcessState, # 运行状态
    'YearMonth': YearMonth, # 年月
    'Warehouse': Warehouse, # 仓库
    'deltag': deltag, # 是否保留
    'SeletcDel': SeletcDel,
    'picname': picname, # 是否图片上传正常
}
upload_params = {
    'ID': ID, # 授权码
    'MAC': MAC,
    'ModelPaper': ModelPaper, # 模板
    'BatchID': BatchID, # 批次号
    'BatchTime': BatchTime, # 批次时间
    'Wordless': Wordless, # 是否有字
    'YearMonth': YearMonth, # 年月
    'Warehouse': Warehouse, # 仓库
}

def get_content_type(filepath):
    return mimetypes.guess_type(filepath)[0] or 'application/octet-stream'

def upload_pic(url, json, pic_path):
    payload = {
        "Content-Type": "image/jpeg",
    }
    for file in sorted(glob.glob(pic_path + "\*.jpg")):
        try:
            files = {'file': (os.path.basename(file), open(file, 'rb'), 'Content-Type: %s' % get_content_type(file))}
        except:
            return os.path.basename(file), None, None
        r = requests.post(url=url, json=json, data=payload, files=files)
        r_json = json.loads(r.json)
        return r_json['status'], r_json['pic'], r_json['Wordless']
    return None, None, None

def work(num):
    with open(config_file, 'r') as f:
        try:
            ID = json.load(f)['ID']
        except:
            input('json异常!')
            break
        if not isinstance(ID, int):
            input('ID类型异常!!')
            break
    # 程序初始绑定
    r = requests.post(author_url, json = json.dumps(author_params), headers = headers)
    try:
        r_json = json.loads(r.json)
        if r_json['status'] != 1: # 授权码异常
            continue

        # 查询配置信息
        r = requests.post(search_url, json = json.dumps(search_params), headers = headers)
        r_json = json.loads(r.json)
        if r_json['status'] != 1: # 查询异常
            continue

        # 加载配置数据
        ModelPaper, Path, PathTag = r_json['ModelPaper'], r_json['Path'], r_json['PathTag']
        BatchID, BatchTime, Wordless = r_json['BatchID'], r_json['BatchTime'], r_json['Wordless']
        ProcessState, YearMonth, Warehouse = r_json['ProcessState'], r_json['YearMonth'], r_json['Warehouse']
        deltag, SeletcDel, picname = r_json['deltag'], r_json['SeletcDel'], r_json['picname']

        # path检测, 更新PathTag
        if not Path: # 空路径直接下次循环
            continue
        if not os.path.exists(Path) or not PathTag: # 如果路径不存在或PathTag为False
            config_params['PathTag'] = False # 更新PathTag为False
            r = requests.post(config_url, json = json.dumps(config_params), headers = headers)
            continue
        # path检测通过, 上传图片
        status, pic, Wordless = upload_pic(upload_url, json.dumps(upload_params), Path)
        if pic is None: # 文件打不开/空
            if status is not None: # 文件异常
                config_params['picname'] = status
                r = requests.post(config_url, json = json.dumps(config_params), headers = headers)
                continue
            if not picname: # path空
                if ProcessState == 'Waiting':
                    continue
                num += 1
                time.sleep(10) # 等待10s
                if ProcessState == 'Doing':
                    if num < 3:
                        continue
                    config_params['ProcessState'] = 'Finish'
                if ProcessState == 'Finish': # 后台自动初始化
                    if num < 3:
                        continue
                r = requests.post(config_url, json = json.dumps(config_params), headers = headers)
                num = 0
                continue
        num = 0
        config_params['picname'] = ""
        config_params['Wordless'] = Wordless
        if ProcessState == 'Waiting':
            config_params['ProcessState'] = 'Doing'
        r = requests.post(config_url, json = json.dumps(config_params), headers = headers)
    except:
        continue

if __name__ == "__main__":
    num = 0 # 用于请求计数
    while True:
        work(num)