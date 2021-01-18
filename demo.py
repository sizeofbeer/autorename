import requests, json, time, uuid, os, glob, mimetypes
from os.path import dirname, abspath

path = dirname(abspath(__file__))
config_file = os.path.join(path, 'init.json')
if not os.path.exists(config_file): # 文件不存在
    with open(config_file, "w") as f:
        json.dump({'ID': 0}, f)

def get_content_type(filepath):
    return mimetypes.guess_type(filepath)[0] or 'application/octet-stream'

def upload_pic(url, datas, pic_path):
    for file in sorted(glob.glob(pic_path + "\*.jpg")):
        try:
            files = {'file': (os.path.basename(file), open(file, 'rb'), 'Content-Type: %s' % get_content_type(file))}
        except:
            return os.path.basename(file), None, None, file
        r = requests.post(url=url, data=datas, files=files)
        r_json = json.loads(r.text)
        # r_json = json.loads(r.text)
        return r_json['status'], r_json['pic'], r_json['Wordless'], file
    return None, None, None, None

if __name__ == "__main__":
    # 参数初始化
    ID, BatchID, SeletcDel = 0, 0, 0 # 从配置文件读取, 批次ID一定不为-1
    MAC = (uuid.uuid1().hex)[-12:].upper() # 本机mac码
    ModelPaperCode, Path, BatchTime, YearMonth, WarehouseCode, picname = '', '', '', '', '', ''
    PathTag, Wordless, ProcessState, deltag = True, True, True, True

    web = 'http://192.168.15.77:2001/EPD/'
    author_url = web + 'AuthorConfig' # 用于授权码注册
    search_url = web + 'PrintAndUpStatusSearch' # 查询配置信息
    config_url = web + 'ClientParamConfig' # 修改配置信息
    upload_url = web + 'PicUpload' # 上传图片
    headers = {'content-type':'application/x-www-form-urlencoded'}
    num = 0 # 用于请求计数
    while True:
        with open(config_file, 'r') as f:
            try:
                ID = json.load(f)['ID']
            except:
                input('json异常!')
                break
            if not isinstance(ID, int):
                input('ID类型异常!!')
                break
        try:
            author_params = {'ID': ID, 'MAC': MAC} # 用在 author_url和 upload_url
            # 程序初始绑定
            print(author_params)
            r = requests.post(author_url, data = author_params, headers = headers)
            r_json = json.loads(r.text)
            if r_json['status'] != 1: # 授权码异常
                continue
            # 查询配置信息
            search_params = {'ID': ID}
            r = requests.post(search_url, data = search_params, headers = headers)
            r_json = json.loads(r.text)
            if r_json['status'] != 1: # 查询异常
                continue

            # 加载配置数据
            ModelPaperCode, Path, PathTag = r_json['ModelPaperCode'], r_json['Path'], r_json['PathTag']
            BatchID, BatchTime, Wordless = r_json['BatchID'], r_json['BatchTime'], r_json['Wordless']
            ProcessState, YearMonth, WarehouseCode = r_json['ProcessState'], r_json['YearMonth'], r_json['WarehouseCode']
            deltag, SeletcDel, picname = r_json['deltag'], r_json['SeletcDel'], r_json['picname']
            config_params = {
                'ID': ID, # 授权码
                'MAC': MAC,
                'ModelPaperCode': ModelPaperCode, # 模板
                'Path': Path, # 路径
                'PathTag': PathTag, # 路径是否有效
                'BatchID': BatchID, # 批次号
                'BatchTime': BatchTime, # 批次时间
                'Wordless': Wordless, # 是否有字
                'ProcessState': ProcessState, # 运行状态
                'YearMonth': YearMonth, # 年月
                'WarehouseCode': WarehouseCode, # 仓库
                'deltag': deltag, # 是否保留
                'SeletcDel': SeletcDel,
                'picname': picname, # 是否图片上传正常
            }
            # path检测, 更新PathTag
            if not Path or (not Wordless and SeletcDel == 0): # 空路径直接下次循环或存在白纸
                continue
            if not os.path.exists(Path) or not PathTag: # 如果路径不存在或PathTag为False
                config_params['PathTag'] = False # 更新PathTag为False
                r = requests.post(config_url, data = config_params, headers = headers)
                continue
            upload_params = {
                'ID': ID, # 授权码
                'MAC': MAC,
                'ModelPaperCode': ModelPaperCode, # 模板
                'BatchID': BatchID, # 批次号
                'BatchTime': BatchTime, # 批次时间
                'Wordless': Wordless, # 是否有字
                'YearMonth': YearMonth, # 年月
                'WarehouseCode': WarehouseCode, # 仓库
            }
            # path检测通过, 上传图片
            status, pic, Wordless, del_file = upload_pic(upload_url, upload_params, Path)
            if pic is None: # 文件打不开/空
                if status is not None: # 文件异常
                    config_params['picname'] = status
                    r = requests.post(config_url, data = config_params, headers = headers)
                    continue
                if not picname: # path空
                    if ProcessState == 'Waiting':
                        continue
                    num += 1
                    time.sleep(5) # 等待10s
                    if ProcessState == 'Doing':
                        if num < 3:
                            continue
                        print('Doing -> Finish')
                        config_params['ProcessState'] = 'Finish'
                    if ProcessState == 'Finish': # 后台自动初始化
                        if num < 3:
                            continue
                        print('Finish -> Waiting')
                    r = requests.post(config_url, data = config_params, headers = headers)
                    num = 0
                    continue
            os.remove(del_file) # 正常删除文件
            num = 0
            config_params['picname'] = ""
            config_params['Wordless'] = Wordless
            if ProcessState == 'Waiting':
                config_params['ProcessState'] = 'Doing'
            r = requests.post(config_url, data = config_params, headers = headers)
        except:
            continue