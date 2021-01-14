import os, json, cv2, re, base64
import time, requests, shapely
from shapely.geometry import Polygon, MultiPoint  # 多边形
import numpy as np
import mimetypes, logging
def get_content_type(filepath):
    return mimetypes.guess_type(filepath)[0] or 'application/octet-stream'

FORMAT = '%(asctime)s-%(levelname)s: %(message)s'
logging.basicConfig(level=logging.INFO, format=FORMAT)
logger = logging.getLogger(__name__)

from os.path import dirname, abspath
path = dirname(abspath(__file__))

# 调用ocr接口获取处理结果
# **测试版本**
def get_ocr_result_aip(image_path):
    url = "http://192.168.15.77:8360/ocr_det_and_rec_api"
    payload = {
        "Content-Type": "image/jpeg",
    }
    file = image_path
    files = {'file': (os.path.basename(file), open(file, 'rb'), 'Content-Type: %s' % get_content_type(file))}
    r = requests.post(url, data=payload, files=files)
    # print(r)
    if r.status_code == 200:
        # result = r.text
        result = json.loads(r.text)
    else:
        logging.info("{} error".format(r.status_code))
        raise ValueError(r.status_code)
    return result
# --计算两个字符串相似度--
def two_str_iou(str1, str2):
    IOU_tag = 0
    if len(str1)==0 or len(str2)==0:
        return IOU_tag
    else:
        sum_value = 0
        for i in range(len(str1)):
            word = str1[i]
            if word in str2:
                sum_value = sum_value + 1
        if 4 <= len(str1) <= 6:
            IOU_tag = (2 * sum_value) / (len(str1) +len(str2)) + 0.01
        else:
            IOU_tag = sum_value / (len(str1) +len(str2) - sum_value)
        # IOU_tag = sum_value / (len(str1) +len(str2) - sum_value)
    return IOU_tag

# --画框--
def drow_box(img, point_bbox, color, thickness):
    for i in range(len(point_bbox)):
        start_id = i
        end_id = (i + 1)%len(point_bbox)
        pt1 = (point_bbox[start_id][0], point_bbox[start_id][1])
        pt2 = (point_bbox[end_id][0], point_bbox[end_id][1])
        cv2.line(img, pt1, pt2, color, thickness)
    return img
# 通过计算ocr识别结果中的box落入所处理模板的value区域的iou，即，box交area/box  = iou
def get_the_most_possible_value(valueArea, ocr_result_content):
    ''' 第一步：初始化返回结果 '''
    find_value_content_dic =[] # 返回的iou匹配处理结果记录
    ''' 格式化area区域，为计算iou做准备 '''
    # 计算iou记录area的标准化处理
    line1 = [valueArea[0][0], valueArea[0][1], valueArea[1][0], valueArea[1][1], valueArea[2][0], valueArea[2][1], valueArea[3][0], valueArea[3][1]]
    # 四边形四个点坐标的一维数组表示，[x0,y0,x1,y1....]
    a = np.array(line1).reshape(4, 2)  # 四边形二维坐标表示
    poly1 = Polygon(a).convex_hull  # python四边形对象，会自动计算四个点，最后四个点顺序为：左上 左下  右下 右上 左上
    ''' 遍历ocr结果，寻找合适框 '''
    #         print(Polygon(a).convex_hull)  # 可以打印看看是不是这样子
    for i in range(len(ocr_result_content)):
        content_dic = ocr_result_content[i]
        # confidence = content_dic['confidence']
        # text = content_dic['text']
        text_box_position = content_dic['text_box_position']
        points = text_box_position
        ''' 格式化box区域，为计算iou做准备 '''
        line2 = [points[0][0], points[0][1], points[1][0], points[1][1], points[2][0], points[2][1], points[3][0],
                 points[3][1]]
        b = np.array(line2).reshape(4, 2)
        poly2 = Polygon(b).convex_hull
        #         print(Polygon(b).convex_hull)
        ''' 合并box坐标，计算box的区域面积 '''
        union_poly = np.concatenate((b, b))  # 合并两个box坐标，变为8*2
        # print(union_poly)
        #         print(MultiPoint(union_poly).convex_hull)  # 包含两四边形最小的多边形点
        ''' 计算iou值 '''
        if not poly1.intersects(poly2):  # 如果两四边形不相交
            iou = 0
        else:
            try:
                inter_area = poly1.intersection(poly2).area  # 相交面积
                #                 print(inter_area)
                # union_area = poly1.area + poly2.area - inter_area
                union_area = MultiPoint(union_poly).convex_hull.area
                #                 print(union_area)
                if union_area == 0:
                    iou = 0
                    # iou = float(inter_area) / (union_area-inter_area)  #错了
                else:
                    iou = float(inter_area) / union_area
                # iou=float(inter_area) /(poly1.area+poly2.area-inter_area)
                # 源码中给出了两种IOU计算方式，第一种计算的是: 交集部分/包含两个四边形最小多边形的面积
                # 第二种： 交集 / 并集（常见矩形框IOU计算方式）
            except shapely.geos.TopologicalError:
                # print('shapely.geos.TopologicalError occured, iou set to 0')
                iou = 0

        ''' 根据iou判断并处理最后结果 '''
        if iou > 0.7:
            if len(find_value_content_dic) <= 0:
                find_value_content_dic.append(content_dic)
            else:
                insert_index = -1
                for point_id in range(len(find_value_content_dic)):
                    # insert_index = point_id
                    value_box_position = find_value_content_dic[point_id]['text_box_position']
                    if text_box_position[0][0] > value_box_position[0][0]:
                        iou_h = (min(text_box_position[3][1], value_box_position[2][1]) - max(text_box_position[0][1],
                                                                                              value_box_position[1][
                                                                                                  1])) / (
                                            max(text_box_position[3][1], value_box_position[2][1]) - min(
                                        text_box_position[0][1], value_box_position[1][1]))
                    else:
                        iou_h = (min(value_box_position[3][1], text_box_position[2][1]) - max(value_box_position[0][1],
                                                                                              text_box_position[1][
                                                                                                  1])) / (
                                            max(value_box_position[3][1], text_box_position[2][1]) - min(
                                        value_box_position[0][1], text_box_position[1][1]))

                    if iou_h > 0.2:
                       if text_box_position[0][0] < value_box_position[0][0] :
                            insert_index = point_id
                            break
                       else:
                           pass
                    elif text_box_position[0][1] < value_box_position[0][1]:
                        insert_index = point_id
                        break
                    else:
                        pass
                        # insert_index =
                if insert_index < 0:
                    find_value_content_dic.append(content_dic)
                else:
                    find_value_content_dic.insert(insert_index, content_dic)

    #     print("index_value, score_index", index_value, score_index)

    return find_value_content_dic
'''
判断是否满足IOU阙值
'''
def is_equal_by_iou(str1, str2, thread):
    IOU_tag = 0
    tag = False
    if len(str1) == 0 or len(str2) == 0:
        pass
    else:
        sum_value = 0
        for i in range(len(str1)):
            word = str1[i]
            if word in str2:
                sum_value = sum_value + 1
        if 3 <= max(len(str1), len(str2)) <= 6:
            IOU_tag = (2 * sum_value) / (len(str1) +len(str2)) + 0.01
        else:
            IOU_tag = sum_value / (len(str1) +len(str2) - sum_value)
        # IOU_tag = sum_value / (len(str1) +len(str2) - sum_value)
        if IOU_tag > thread:
            tag = True
    return tag

'''
假设固定语义字符识别结果优, 计算相似度
获取最优置信度下的点
element: "语义1": [position]
list: [element1, element2, ...]
'''
def confirm_target_points(choose_words, content, confidence_thread, iou_thread):
    usable_point = [None] * len(choose_words)
    usable_txt = [None] * len(choose_words)
    usable_conf = [None] * len(choose_words)
    
    for i, us_word in enumerate(choose_words):
        temp_confidence = 0.0
        tag_count = 0
        for content_dic in content:
            text_box_position = content_dic['text_box_position']
            confidence = content_dic['confidence']
            text = content_dic['text']
            text = text.replace('：', ':').replace('，', ',').replace('（', '(').replace('）', ')').lower()
            ''' 新增逻辑 '''
            if us_word == text:
                temp_confidence = float(confidence)
                usable_point[i] = text_box_position
                usable_txt[i] = text
                usable_conf[i] = temp_confidence
                break
            if (float(confidence) > confidence_thread) and is_equal_by_iou(text, us_word, iou_thread):
                if float(confidence) > temp_confidence:
                    if tag_count != 0 and ((len(text) > (1 + len(us_word))) or (len(us_word) > (1 + len(text)))):
                        pass
                    else:
                        temp_confidence = float(confidence)
                        usable_point[i] = text_box_position
                        usable_txt[i] = text
                        usable_conf[i] = temp_confidence
                        tag_count += 1
            else:
                continue
    return usable_point, usable_txt, usable_conf

def special_target_points(choose_words, content, confidence_thread, iou_thread):
    usable_point = [None] * len(choose_words)
    usable_txt = [None] * len(choose_words)
    usable_conf = [None] * len(choose_words)
    
    for i, us_word in enumerate(choose_words):
        temp_confidence = 0.0
        tag_count = 0
        for content_dic in content:
            text_box_position = content_dic['text_box_position']
            confidence = content_dic['confidence']
            text = content_dic['text']
            num = 0
            for ch in us_word:
                if ch in text:
                    num += 1
            #print(text, num)
            if num < (len(us_word)-1):
                continue
            #print(text, us_word, num)
            if (float(confidence) > confidence_thread):
                if float(confidence) > temp_confidence:
                    temp_confidence = float(confidence)
                    usable_point[i] = text_box_position
                    usable_txt[i] = text
                    usable_conf[i] = temp_confidence
                    tag_count += 1
            else:
                continue
    return usable_point, usable_txt, usable_conf

def special_target_points_revise(choose_words, content, confidence_thread, iou_thread):
    usable_point = [None] * len(choose_words)
    usable_txt = [None] * len(choose_words)
    usable_conf = [None] * len(choose_words)
    
    for i, us_word in enumerate(choose_words):
        temp_confidence = 0.0
        tag_count = 0
        for content_dic in content:
            text_box_position = content_dic['text_box_position']
            confidence = content_dic['confidence']
            text = content_dic['text']
            text = text.replace('：', ':').replace('，', ',').replace('（', '(').replace('）', ')').lower()
            text = "".join(re.findall(re.compile('[\u4e00-\u9fa5]'), text)).replace('栋', '拣').replace('探', '拣')
            # print(text, len(text), len(us_word))
            if (float(confidence) > confidence_thread) and is_equal_by_iou(text, us_word, iou_thread):
                if float(confidence) > temp_confidence:
                    if tag_count != 0 and ((len(text) < (1 + len(us_word))) or (len(text) > (len(us_word) - 1))):
                        pass
                    else:
                        temp_confidence = float(confidence)
                        usable_point[i] = text_box_position
                        usable_txt[i] = text
                        usable_conf[i] = temp_confidence
                        tag_count += 1
            else:
                continue
    return usable_point, usable_txt, usable_conf

def best_point_by_confience(choose_indexs, usable_conf, usable_point):
    points, temp_conf = None, None
    for i in choose_indexs:
        if usable_point[i] is not None:
            if temp_conf is None:
                points = usable_point[i]
                temp_conf = usable_conf[i]
            else:
                if temp_conf < usable_conf[i]:
                    points = usable_point[i]
                    temp_conf = usable_conf[i]
    return points, temp_conf

def best_x_coord(choose_left_indexs, choose_right_indexs, usable_conf, usable_point):
    x_coord = -1
    points_left, conf_left = best_point_by_confience(choose_left_indexs, usable_conf, usable_point)
    points_right, conf_right = best_point_by_confience(choose_right_indexs, usable_conf, usable_point)
    if points_left is None:
        if points_right is not None:
            x_coord = points_right[1][0]
    else:
        if points_right is not None:
            if conf_left > conf_right:
                x_coord = points_left[3][0]
            else:
                x_coord = points_right[1][0]
        else:
            x_coord = points_left[3][0]
    return x_coord

def best_y_coord(x_coord, choose_up_indexs, choose_down_indexs, usable_conf, usable_point):
    y_coord = -1
    usable_k, usable_b = 0, 0
    points_up, conf_up = best_point_by_confience(choose_up_indexs, usable_conf, usable_point)
    points_down, conf_down = best_point_by_confience(choose_down_indexs, usable_conf, usable_point)
    if points_up is None:
        if points_down is not None:
            points = points_down
            if int(points[3][0] - points[2][0]) == 0:
                y_coord = points[3][0]
            else:
                usable_k = (points[3][1] - points[2][1]) / (points[3][0] - points[2][0])
                usable_b = points[3][1] - usable_k * points[3][0]
                y_coord = int(usable_k * x_coord + usable_b)
    else:   
        if points_down is not None:
            if conf_up > conf_down:
                points = points_up
                if int(points[0][0] - points[1][0]) == 0:
                    y_coord = points[0][0]
                else:
                    usable_k = (points[0][1] - points[1][1]) / (points[0][0] - points[1][0])
                    usable_b = points[0][1] - usable_k * points[0][0]
                    y_coord = int(usable_k * x_coord + usable_b)
            else:
                points = points_down
                if int(points[3][0] - points[2][0]) == 0:
                    y_coord = points[3][0]
                else:
                    usable_k = (points[3][1] - points[2][1]) / (points[3][0] - points[2][0])
                    usable_b = points[3][1] - usable_k * points[3][0]
                    y_coord = int(usable_k * x_coord + usable_b)
        else:
            points = points_up
            if int(points[0][0] - points[1][0]) == 0:
                y_coord = points[0][0]
            else:
                usable_k = (points[0][1] - points[1][1]) / (points[0][0] - points[1][0])
                usable_b = points[0][1] - usable_k * points[0][0]
                y_coord = int(usable_k * x_coord + usable_b)
    return y_coord

def best_x_y_point(weight, point_bbox, choose_left_indexs, choose_right_indexs, choose_left_indexs1, choose_right_indexs1,
                            choose_up_indexs, choose_down_indexs, choose_up_indexs1, choose_down_indexs1, usable_conf, usable_point):
    if choose_left_indexs or choose_right_indexs:
        point_bbox[0][0] = best_x_coord(choose_left_indexs, choose_right_indexs, usable_conf, usable_point)
        point_bbox[3][0] = point_bbox[0][0]
    if point_bbox[0][0] == -1:
        point_bbox[0][0] = 5
        point_bbox[3][0] = point_bbox[0][0]
    if choose_left_indexs1 or choose_right_indexs1:
        point_bbox[1][0] = best_x_coord(choose_left_indexs1, choose_right_indexs1, usable_conf, usable_point)
        point_bbox[2][0] = point_bbox[1][0]
    if point_bbox[1][0] == -1:
        point_bbox[1][0] = int(weight) - 5
        point_bbox[2][0] = point_bbox[1][0]

    # y轴坐标
    point_bbox[0][1] = best_y_coord(point_bbox[0][0], choose_up_indexs, choose_down_indexs, usable_conf, usable_point)
    point_bbox[1][1] = best_y_coord(point_bbox[1][0], choose_up_indexs, choose_down_indexs, usable_conf, usable_point)

    point_bbox[2][1] = best_y_coord(point_bbox[2][0], choose_up_indexs1, choose_down_indexs1, usable_conf, usable_point)
    point_bbox[3][1] = best_y_coord(point_bbox[3][0], choose_up_indexs1, choose_down_indexs1, usable_conf, usable_point)
    return point_bbox

def process_infor_hilti(result_content, image):
    h, w = image.shape[:2]
    two_str_iou_thread = 0.85
    confidence_thread = 0.55
    ''' 第一步：找value的区域信息，即：areas_box = [point_bbox_1, point_bbox_2, point_bbox_13] '''
    ''' 1.1 初始化区域 '''
    # 1、装运总单号Pack Slip No
    point_bbox_1 = [[-1,-1], [-1,-1], [-1,-1], [-1,-1]]

    choose_words = ['送货/发票清单', '捡货单编号:', '政府发票号码:', "发票签收:",
                    '订单日期:', '要求发货日期:', 'website:www.hilti.cn', '页号:',
                    '收货状况:', '公司盖章:', '客户编号:', '订单编号:',
                    '工地/项目:', '联系方式:', '采购订单:', '核准人:',
                    '服务热线:800-820-2585400-820-2585', '送货地址:']
    special_words = ['拣货单']
    ''' 输出目标点坐标和识别内容 '''
    usable_point, usable_txt, usable_conf = confirm_target_points(choose_words, result_content, confidence_thread, two_str_iou_thread)
    ''' 1.2 优化最佳区域 '''
    if usable_point[0] is not None or usable_point[1] is not None:
        if usable_point[2] is not None or usable_point[3] is not None:
            ''' 确定左侧x轴 '''
            choose_left_indexs = []
            choose_right_indexs = [1, 3, 4, 5]
            ''' 确定右侧x轴 '''
            choose_left_indexs1 = [8, 9, 14]
            choose_right_indexs1 = [6]
            ''' 确定上侧y轴 '''
            choose_up_indexs = [1]
            choose_down_indexs = [4]
            ''' 确定下侧y轴 '''
            choose_up_indexs1 = []
            choose_down_indexs1 = [1, 5]
            point_bbox_1 = best_x_y_point(w, point_bbox_1, choose_left_indexs, choose_right_indexs, choose_left_indexs1, choose_right_indexs1,
                                    choose_up_indexs, choose_down_indexs, choose_up_indexs1, choose_down_indexs1, usable_conf, usable_point)
        else:
            ''' 确定左侧x轴 '''
            choose_left_indexs = []
            choose_right_indexs = [1, 10, 11]
            ''' 确定右侧x轴 '''
            choose_left_indexs1 = [4, 5, 6]
            choose_right_indexs1 = []
            ''' 确定上侧y轴 '''
            choose_up_indexs = [1, 5, 13]
            choose_down_indexs = [4, 11]
            ''' 确定下侧y轴 '''
            choose_up_indexs1 = [12]
            choose_down_indexs1 = [1, 5]
            point_bbox_1 = best_x_y_point(w, point_bbox_1, choose_left_indexs, choose_right_indexs, choose_left_indexs1, choose_right_indexs1,
                                    choose_up_indexs, choose_down_indexs, choose_up_indexs1, choose_down_indexs1, usable_conf, usable_point)
    else:
        special_point, special_txt, special_conf = special_target_points_revise(special_words, result_content, confidence_thread, two_str_iou_thread)
        # print(special_point)
        if special_point[0] is not None:
            usable_point = usable_point + special_point
            usable_txt = usable_txt + special_txt
            usable_conf = usable_conf + special_conf
            if usable_point[9] is not None or usable_point[15] is not None:
                ''' 确定左侧x轴 '''
                choose_left_indexs = [-1, 9, 15]
                choose_right_indexs = []
                ''' 确定右侧x轴 '''
                choose_left_indexs1 = [6, 16, 17]
                choose_right_indexs1 = []
                ''' 确定上侧y轴 '''
                choose_up_indexs = [-1]
                choose_down_indexs = []
                ''' 确定下侧y轴 '''
                choose_up_indexs1 = []
                choose_down_indexs1 = [-1]
                point_bbox_1 = best_x_y_point(w, point_bbox_1, choose_left_indexs, choose_right_indexs, choose_left_indexs1, choose_right_indexs1,
                                        choose_up_indexs, choose_down_indexs, choose_up_indexs1, choose_down_indexs1, usable_conf, usable_point)
            else:
                ''' 确定左侧x轴 '''
                choose_left_indexs = [-1, 5, 10]
                choose_right_indexs = []
                ''' 确定右侧x轴 '''
                choose_left_indexs1 = [4, 6, 11, 16]
                choose_right_indexs1 = []
                ''' 确定上侧y轴 '''
                choose_up_indexs = [-1]
                choose_down_indexs = []
                ''' 确定下侧y轴 '''
                choose_up_indexs1 = []
                choose_down_indexs1 = [-1]
                point_bbox_1 = best_x_y_point(w, point_bbox_1, choose_left_indexs, choose_right_indexs, choose_left_indexs1, choose_right_indexs1,
                                        choose_up_indexs, choose_down_indexs, choose_up_indexs1, choose_down_indexs1, usable_conf, usable_point)

    ''' 1.3 展示最佳区域 '''
    # 1、装运总单号Pack Slip No
    image = drow_box(image, point_bbox_1, (255, 0, 0), 5)

    ''' 1.4 收集最佳区域 '''
    areas_box = [point_bbox_1]

    ''' 第二步：组合value值'''
    ''' 2.1 初始化value值 '''
    value_sum_numble = len(areas_box)  # value的个数
    result_str = [""] * value_sum_numble # 初始化value值

    values_of_ocr_boxes = [[]] * value_sum_numble  # 初始化value值所在区域，用来记录最大可能落入该区域的所有ocr识别结果
    ''' 分别对每个区域找落入该区域的所有ocr节点 '''
    for i in range(value_sum_numble):
        point_bbos = areas_box[i]
        # 属于该区域的所有ocr识别结果节点信息values_of_ocr_boxes_in_point_bbos = [{'confidence': '0.97679645', 'text': 'Meters/bonwe', 'text_box_position': [[201, 47], [412, 47], [412, 71], [201, 71]]},...]
        values_of_ocr_boxes_in_point_bbos = get_the_most_possible_value(point_bbos, result_content)
        values_of_ocr_boxes[i] = values_of_ocr_boxes_in_point_bbos # 将该节点信息记录在values_of_ocr_boxes列表中
        # 依次获取落入该区域的ocr识别结果的text，作为最终输出的字段信息结果。
        if len(values_of_ocr_boxes_in_point_bbos) > 0:
            # 若获取到了最佳落入该区域的ocr结果，则依次组合
            for j in range(len(values_of_ocr_boxes_in_point_bbos)):
                content_dic = values_of_ocr_boxes_in_point_bbos[j]
                text = content_dic['text']
    # print(values_of_ocr_boxes)
    
    for i in range(len(values_of_ocr_boxes)):
        result_text = ""
        area_ocr_result = values_of_ocr_boxes[i]
        for j in range(len(area_ocr_result)):
            content_dic_ocr = area_ocr_result[j]
            text_box_position1 = content_dic_ocr['text_box_position']
            text1 = content_dic_ocr['text']
            # image = drow_box(image, text_box_position1, (0, 255, 0), 5)
            result_text += text1
        result_text = "".join(re.findall(r"\d+\.?\d*", result_text))
        if len(result_text) > 9:
            start = len(result_text) - 9
            result_text = result_text[start:]
        result_str[i] = result_text
    # cv2.imwrite("1.jpg", image)
    # cv2.imshow("eer", image)
    # cv2.waitKey(0)
    # print(result_str, areas_box, values_of_ocr_boxes)
    return result_str, areas_box, values_of_ocr_boxes

def get_hilti_value(path_photo):
    image = cv2.imread(path_photo)
    result_content = get_ocr_result_aip(path_photo)['result']
    # for box_content in result_content:
    #     print(box_content)
    #     point_box = box_content['text_box_position']
    #     image = drow_box(image, point_box, (255, 0, 0), 5)
    # cv2.imwrite("1.jpg", image)
    result_str, areas_box, values_of_ocr_boxes = process_infor_hilti(result_content, image)
    return result_str, areas_box, values_of_ocr_boxes

import pyzbar.pyzbar as pyzbar
def process_infor_warehouse(result_content, image):
    h, w = image.shape[:2]
    two_str_iou_thread = 0.85
    confidence_thread = 0.7
    bar_code = None
    ''' 第一步：找value的区域信息，即：areas_box = [point_bbox_1, point_bbox_2, point_bbox_13] '''
    ''' 1.1 初始化区域 '''
    # 1、装运总单号Pack Slip No
    point_bbox_1 = [[-1,-1], [-1,-1], [-1,-1], [-1,-1]]

    choose_words = ['采购订单号:', '实际交货期', '预计到货期', '备注', '计划的盘点日期', '实际存货参考']
    special_words = ['创建,']
    ''' 输出目标点坐标和识别内容 '''
    usable_point, usable_txt, usable_conf = confirm_target_points(choose_words, result_content, confidence_thread, two_str_iou_thread)
    special_point, special_txt, special_conf = special_target_points(special_words, result_content, confidence_thread, two_str_iou_thread)
    usable_point += special_point
    usable_txt += special_txt
    usable_conf += special_conf
    if (usable_txt[0] and usable_txt[1]) or usable_txt[2]:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        texts = pyzbar.decode(gray)
        if texts:
            bar_code = texts[-1].data.decode("utf-8")
        else:
            bar_code = ''
        ''' 1.2 优化最佳区域 '''
        # point_bbox_1
        ''' 确定左侧x轴 '''
        choose_left_indexs = [0, 2]
        choose_right_indexs = []
        ''' 确定右侧x轴 '''
        choose_left_indexs1 = [1]
        choose_right_indexs1 = [2]
        ''' 确定上侧y轴 '''
        choose_up_indexs = []
        choose_down_indexs = [1, 2]
        ''' 确定下侧y轴 '''
        choose_up_indexs1 = [3]
        choose_down_indexs1 = []
        point_bbox_1 = best_x_y_point(w, point_bbox_1, choose_left_indexs, choose_right_indexs, choose_left_indexs1, choose_right_indexs1,
                                choose_up_indexs, choose_down_indexs, choose_up_indexs1, choose_down_indexs1, usable_conf, usable_point)
    elif usable_txt[4] or (usable_txt[5] and usable_txt[6]):
        ''' 1.2 优化最佳区域 '''
        # point_bbox_1
        ''' 确定左侧x轴 '''
        choose_left_indexs = []
        choose_right_indexs = [4, 5, 6]
        ''' 确定右侧x轴 '''
        choose_left_indexs1 = []
        choose_right_indexs1 = []
        ''' 确定上侧y轴 '''
        choose_up_indexs = [4]
        choose_down_indexs = [6]
        ''' 确定下侧y轴 '''
        choose_up_indexs1 = [5]
        choose_down_indexs1 = [4]
        point_bbox_1 = best_x_y_point(w, point_bbox_1, choose_left_indexs, choose_right_indexs, choose_left_indexs1, choose_right_indexs1,
                                choose_up_indexs, choose_down_indexs, choose_up_indexs1, choose_down_indexs1, usable_conf, usable_point)
    else:
        print('待增加功能')
    ''' 1.3 展示最佳区域 '''
    # 1、装运总单号Pack Slip No
    image = drow_box(image, point_bbox_1, (255, 0, 0), 5)
    ''' 1.4 收集最佳区域 '''
    areas_box = [point_bbox_1]

    ''' 第二步：组合value值'''
    ''' 2.1 初始化value值 '''
    value_sum_numble = len(areas_box)  # value的个数
    result_str = [""] * value_sum_numble # 初始化value值

    values_of_ocr_boxes = [[]] * value_sum_numble  # 初始化value值所在区域，用来记录最大可能落入该区域的所有ocr识别结果
    ''' 分别对每个区域找落入该区域的所有ocr节点 '''
    for i in range(value_sum_numble):
        point_bbos = areas_box[i]
        # 属于该区域的所有ocr识别结果节点信息values_of_ocr_boxes_in_point_bbos = [{'confidence': '0.97679645', 'text': 'Meters/bonwe', 'text_box_position': [[201, 47], [412, 47], [412, 71], [201, 71]]},...]
        values_of_ocr_boxes_in_point_bbos = get_the_most_possible_value(point_bbos, result_content)
        values_of_ocr_boxes[i] = values_of_ocr_boxes_in_point_bbos # 将该节点信息记录在values_of_ocr_boxes列表中
        # # 依次获取落入该区域的ocr识别结果的text，作为最终输出的字段信息结果。
        # if len(values_of_ocr_boxes_in_point_bbos) > 0:
        #     # 若获取到了最佳落入该区域的ocr结果，则依次组合
        #     for j in range(len(values_of_ocr_boxes_in_point_bbos)):
        #         content_dic = values_of_ocr_boxes_in_point_bbos[j]
        #         text = content_dic['text']
    ''' 识别校正处理 '''
    # print(values_of_ocr_boxes)
    for i in range(len(values_of_ocr_boxes)):
        result_text = ""
        up_x, down_x = -1, -1
        area_ocr_result = values_of_ocr_boxes[i]
        for j in range(len(area_ocr_result)):
            content_dic_ocr = area_ocr_result[j]
            text_box_position = content_dic_ocr['text_box_position']
            text = content_dic_ocr['text']
            if up_x == -1:
                down_x = text_box_position[2][1]
                up_x = text_box_position[0][1]
                result_text = text
                continue
            point_centre = text_box_position[0][1] + int((text_box_position[2][1] - text_box_position[0][1]) / 2)
            if point_centre > up_x and point_centre < down_x:
                down_x = max(text_box_position[2][1], down_x)
                up_x = min(text_box_position[0][1], up_x)
                result_text += text
            else:
                if text_box_position[0][1] < up_x:
                    down_x = text_box_position[2][1]
                    up_x = text_box_position[0][1]
                    result_text = text
        result_str[i] = result_text.replace('：', ':').replace('.', '-').lstrip(':')
    if bar_code is not None:
        result_str.append(bar_code)
    # out_path = os.path.join(path, 'sources')
    # out_file = os.path.join(path, '1.jpg')
    # cv2.imwrite(out_file, image)
    # cv2.imshow("eer", image)
    # cv2.waitKey(0)
    # print(result_str, areas_box, values_of_ocr_boxes)
    return result_str, areas_box, values_of_ocr_boxes

def get_warehouse_value(path_photo):
    image = cv2.imread(path_photo)
    result_content = get_ocr_result_aip(path_photo)['result']
    # for box_content in result_content:
    #     print(box_content)
    #     point_box = box_content['text_box_position']
    #     image = drow_box(image, point_box, (255, 0, 0), 5)
    # cv2.imwrite("1.jpg", image)
    result_str, areas_box, values_of_ocr_boxes = process_infor_warehouse(result_content, image)
    return result_str, areas_box, values_of_ocr_boxes