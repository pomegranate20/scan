from cv2 import boundingRect, imread, cvtColor, COLOR_BGR2GRAY, GaussianBlur, Canny, findContours, RETR_EXTERNAL, CHAIN_APPROX_SIMPLE, drawContours, contourArea, arcLength, approxPolyDP
from cv2 import threshold, THRESH_BINARY_INV, THRESH_OTSU, bitwise_and, countNonZero, putText, FONT_HERSHEY_SIMPLEX, imshow, waitKey, imwrite, destroyAllWindows
from os.path import exists
from os import mkdir
from time import strftime, localtime, time
from imutils.perspective import four_point_transform
from numpy import arange, zeros
from tkinter import filedialog, simpledialog, messagebox
from tkinter import *
from ttkbootstrap import Text
from requests import post
from base64 import b64encode
from cv2 import RETR_LIST, ADAPTIVE_THRESH_MEAN_C, adaptiveThreshold, THRESH_BINARY
from numpy import zeros, float32, argmax, argmin
from os.path import exists
from os import mkdir
from time import strftime, localtime, sleep, time
from skimage.filters import threshold_local, thresholding
from imutils import resize
from ttkbootstrap import Label, Button
from winsound import SND_ASYNC, PlaySound
import operator
from PIL import Image
from functools import reduce
from tkinter.messagebox import *


from login import *

if not exists('exam'):
    mkdir("exam")


def judge():
    def file():
        filename = filedialog.askopenfilename()
        filename = filename.replace("/", "\\")
        return filename

    def sort_contours(contours, method="l2r"):
        # 用于给轮廓排序，l2r, r2l, t2b, b2t
        reverse = False
        i = 0
        if method == "r2l" or method == "b2t":
            reverse = True
        if method == "t2b" or method == "b2t":
            i = 1

        boundingBoxes = [boundingRect(c) for c in contours]
        (contours, boundingBoxes) = zip(
            *sorted(zip(contours, boundingBoxes), key=lambda a: a[1][i], reverse=reverse))
        return contours, boundingBoxes

    #  正确答案
    dic = {'A': 0, "B": 1, "C": 2, "D": 3, "E": 4}

    r = simpledialog.askstring("输入答案", "请输入正确答案：例如'AAAAA'")
    list1 = list(r)

    right_key = {0: dic[list1[0]], 1: dic[list1[1]],
                 2: dic[list1[2]], 3: dic[list1[3]], 4: dic[list1[4]]}

    # 输入图像
    img = imread(file())

    img_copy = img.copy()
    img_gray = cvtColor(img, COLOR_BGR2GRAY)
    # cvshow('img-gray', img_gray)

    # 图像预处理
    # 高斯降噪
    img_gaussian = GaussianBlur(img_gray, (5, 5), 1)
    # cvshow('gaussianblur', img_gaussian)
    # canny边缘检测
    img_canny = Canny(img_gaussian, 80, 150)
    # cvshow('canny', img_canny)

    # 轮廓识别——答题卡边缘识别
    cnts, hierarchy = findContours(
        img_canny, RETR_EXTERNAL, CHAIN_APPROX_SIMPLE)
    drawContours(img_copy, cnts, -1, (0, 0, 255), 3)
    # cvshow('contours-show', img_copy)

    docCnt = None

    # 确保检测到了
    if len(cnts) > 0:
        # 根据轮廓大小进行排序
        cnts = sorted(cnts, key=contourArea, reverse=True)

        # 遍历每一个轮廓
        for c in cnts:
            # 近似
            peri = arcLength(c, True)  # arclength 计算一段曲线的长度或者闭合曲线的周长；
            # 第一个参数输入一个二维向量，第二个参数表示计算曲线是否闭合

            approx = approxPolyDP(c, 0.02 * peri, True)
            # 用一条顶点较少的曲线/多边形来近似曲线/多边形，以使它们之间的距离<=指定的精度；
            # c是需要近似的曲线，0.02*peri是精度的最大值，True表示曲线是闭合的

            # 准备做透视变换
            if len(approx) == 4:
                docCnt = approx
                break

    # 透视变换——提取答题卡主体
    docCnt = docCnt.reshape(4, 2)
    warped = four_point_transform(img_gray, docCnt)
    # cvshow('warped', warped)

    # 轮廓识别——识别出选项
    thresh = threshold(
        warped, 0, 255, THRESH_BINARY_INV | THRESH_OTSU)[1]
    # cvshow('thresh', thresh)
    thresh_cnts, _ = findContours(
        thresh, RETR_EXTERNAL, CHAIN_APPROX_SIMPLE)
    w_copy = warped.copy()
    drawContours(w_copy, thresh_cnts, -1, (0, 0, 255), 2)
    # cvshow('warped_contours', w_copy)

    questionCnts = []
    # 遍历，挑出选项的cnts
    for c in thresh_cnts:
        (x, y, w, h) = boundingRect(c)
        ar = w / float(h)
        # 根据实际情况指定标准
        if w >= 20 and h >= 20 and ar >= 0.9 and ar <= 1.1:
            questionCnts.append(c)

    # 检查是否挑出了选项
    w_copy2 = warped.copy()
    drawContours(w_copy2, questionCnts, -1, (0, 0, 255), 2)
    # cvshow('questionCnts', w_copy2)

    # 检测每一行选择的是哪一项，并将结果储存在元组bubble中，记录正确的个数correct
    # 按照从上到下t2b对轮廓进行排序
    questionCnts = sort_contours(questionCnts, method="t2b")[0]
    correct = 0
    # 每行有5个选项
    for (i, q) in enumerate(arange(0, len(questionCnts), 5)):
        # 排序
        cnts = sort_contours(questionCnts[q:q+5])[0]

        bubble = None
        # 得到每一个选项的mask并填充，与正确答案进行按位与操作获得重合点数
        for (j, c) in enumerate(cnts):
            mask = zeros(thresh.shape, dtype='uint8')
            drawContours(mask, [c], -1, 255, -1)
            # cvshow('mask', mask)

            # 通过按位与操作得到thresh与mask重合部分的像素数量
            bitand = bitwise_and(thresh, thresh, mask=mask)
            totalPixel = countNonZero(bitand)

            if bubble is None or bubble[0] < totalPixel:
                bubble = (totalPixel, j)

        k = bubble[1]
        color = (0, 0, 255)
        if k == right_key[i]:
            correct += 1
            color = (0, 255, 0)

        # 绘图
        warped = drawContours(warped, [cnts[right_key[i]]], -1, color, 3)
    # cvshow('final', warped)

    # 计算最终得分并在图中标注
    score = (correct / 5.0) * 100
    # print(f"Score: {score}%")
    putText(warped, f"Score: {score}%", (10, 30),
            FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
    # cv.imshow("Original", img)
    imshow("Exam", warped)
    waitKey(0)
    path = 'exam'

    name = str(strftime('%Y-%m-%d_%H-%M-%S',
                        localtime(time())))+".jpg"
    imwrite(filename=path+"\\"+name, img=warped)
    destroyAllWindows()


if not exists('scanned'):
    mkdir("scanned")


def file():
    filename = filedialog.askopenfilename()
    filename = filename.replace("/", "\\")
    return filename


def rectify(h):
    h = h.reshape((4, 2))  # 改变数组的形状，变成4*2形状的数组
    hnew = zeros((4, 2), dtype=float32)  # 创建一个4*2的零矩阵
    # 确定检测文档的四个顶点
    add = h.sum(1)
    hnew[0] = h[argmin(add)]  # argmin()函数是返回最大数的索引
    hnew[2] = h[argmax(add)]

    diff = diff(h, axis=1)  # 沿着制定轴计算第N维的离散差值
    hnew[1] = h[argmin(diff)]
    hnew[3] = h[argmax(diff)]

    return hnew


def transform():
    # 转换大小 保存副本
    img = imread(file())
    orig = img.copy()
    ratio = img.shape[0] / 500.0
    img = resize(img, height=500)

    # 预处理 转灰度图->滤波->边缘检测
    gray = cvtColor(img, COLOR_BGR2GRAY)
    gray = GaussianBlur(gray, (5, 5), 0)
    edge = Canny(gray, 75, 200)

    # 寻找轮廓 按照面积排序
    cnt, _ = findContours(edge, RETR_LIST, CHAIN_APPROX_SIMPLE)
    cnt = sorted(cnt, key=contourArea, reverse=True)[:5]
    for c in cnt:
        # 用vertex来记录每个轮廓的顶点
        peri = arcLength(c, True)
        vertex = approxPolyDP(c, 0.02 * peri, True)
        # 顶点个数是4 说明找到了四边形
        if len(vertex) == 4:
            break
    return orig, vertex, img, cnt, ratio


def gray():
    orig, vertex, img, cnt, ratio = transform()
    try:
        for c in cnt:
            # 用vertex来记录每个轮廓的顶点
            peri = arcLength(c, True)
            vertex = approxPolyDP(c, 0.02 * peri, True)
            # 顶点个数是4 说明找到了四边形
            if len(vertex) == 4:
                break
            # 转换大小 保存副本
            # 透视变换
        transformed = four_point_transform(
            orig, vertex.reshape(4, 2) * ratio)
        transformed = cvtColor(transformed, COLOR_BGR2GRAY)
    except:
        PlaySound('alert', SND_ASYNC)
        sleep(0.6)
        warning = Tk()
        Label(warning, t1="未识别到文档，已为您将原图片进行黑白处理",
              style="warning", compound="center", background="#D9E3F1").pack()
        dst = cvtColor(img, COLOR_BGR2GRAY)
        # 自适应阈值
        th = adaptiveThreshold(
            dst, 255, ADAPTIVE_THRESH_MEAN_C, THRESH_BINARY, 11, 5)
        path = 'scanned'
        name = str(strftime('%Y%m%d_%H%M%S', localtime(time())))+".jpg"
        imshow("scanned", th)
        imwrite(filename=path+"\\"+name, img=th)
    else:
        dst = cvtColor(img, COLOR_BGR2GRAY)
        # 自适应阈值
        th = adaptiveThreshold(
            dst, 255, ADAPTIVE_THRESH_MEAN_C, THRESH_BINARY, 11, 5)
        # 动态阈值
        T = threshold_local(transformed, 15, method='gaussian', offset=5)
        transformed = (transformed > T).astype('uint8') * 255
        # flag=1
        ans = resize(transformed, height=500)
        path = 'scanned'
        imshow("scanned", ans)
        name = str(strftime('%Y%m%d_%H%M%S', localtime(time())))+".jpg"
        # imwrite(filename=name,img=ans)
        root2 = Tk()
        Label(root2, text=('已为您将图片保存至"' + path + "\\"+name)).pack()
        Button(root2, text=("我知道了"), command=root2.destroy).pack()

        root2.mainloop()

        imwrite(filename=path+"\\"+name, img=ans)
        waitKey(0)
        destroyAllWindows()


def ocr(img_path: str) -> list:
    '''
    根据图片路径，将图片转为文字，返回识别到的字符串列表

    '''
    # 请求头
    headers = {
        'Host': 'cloud.baidu.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36 Edg/89.0.774.76',
        'Accept': '*/*',
        'Origin': 'https://cloud.baidu.com',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Referer': 'https://cloud.baidu.com/product/ocr/general',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    }
    # 打开图片并对其使用 base64 编码
    with open(img_path, 'rb') as f:
        img = b64encode(f.read())
    data = {
        'image': 'data:image/jpeg;base64,'+str(img)[2:-1],
        'image_url': '',
        'type': 'https://aip.baidubce.com/rest/2.0/ocr/v1/general_basic',
        'detect_direction': 'false'
    }
    # 开始调用 ocr 的 api
    response = post(
        'https://cloud.baidu.com/aidemo', headers=headers, data=data)

    # 设置一个空的列表，后面用来存储识别到的字符串
    ocr_text = []
    result = response.json()['data']
    if not result.get('words_result'):
        return []

    # 将识别的字符串添加到列表里面
    for r in result['words_result']:
        t1 = r['words'].strip()
        ocr_text.append(t1)
    # 返回字符串列表
    return ocr_text


def rec():
    # content 是识别后得到的结果
    content = "".join(ocr(file()))
    # 输出结果

    root2 = Tk()
    t1 = Text(root2)
    t1.pack()
    t1.insert(1.0, content)

    def cutJob():                            # Cut方法
        print("Cut operation in progress...")
        copyJob()                            # 复制选取文字
        t1.delete(SEL_FIRST, SEL_LAST)      # 删除选取文字

    def copyJob():
        print("Copy operation in process...")
        try:
            t1.clipboard_clear()
            copyText = t1.get(SEL_FIRST, SEL_LAST)
            t1.clipboard_append(copyText)
        except TclError:
            print("Not selected...")

    def pasteJob():
        print("Paste operation is in progress...")
        try:
            copyText = t1.selection_get(selection="CLIPBOARD")
            t1.insert(INSERT, copyText)
        except TclError:
            print("No data on the clipboard")

    def showPopupMenu(event):
        print("Show pop-up menu...")
        popupmenu.post(event.x_root, event.y_root)

    root = Tk()
    root.title("apidemos.com")
    root.geometry("0x0")

    popupmenu = Menu(root, tearoff=False)
    # 在弹出菜单内建立三个命令列表
    popupmenu.add_command(label="Cut", command=cutJob)
    popupmenu.add_command(label="Copy", command=copyJob)
    popupmenu.add_command(label="Paste", command=pasteJob)
    # 单击鼠标右键绑定显示弹出菜单
    root2.bind("<Button-3>", showPopupMenu)
    root2.mainloop()


def pri(msg):
    mx1 = showinfo(title='消息提示框', message=msg)


def pri1(msg):
    mx2 = showwarning(title='消息提示框', message=msg)


def makeFace(facename, msg):
    pri(msg)  # 显示提示信息
#     cv2.namedWindow("face_recognition")
#     cv2.waitKey(0)
    cap = cv2.VideoCapture(0)  # 打开摄像头
    while (cap.isOpened()):  # 如果摄像头处于打开状态，则...
        try:
            ret, img = cap.read()  # 读取图像
            if ret == True:  # 读取成功
                cv2.imshow("face_recognition", img)  # 显示图像
                k = cv2.waitKey(100)  # 每0.1秒读一次键盘
                if k == ord("z") or k == ord("Z"):  # 如果输入z
                    cv2.imwrite(facename, img)  # 把读取的img保存至facename文件
                    # 读取刚刚保存的facename文件至image变量，作为下面人脸识别函数的参数
                    image = cv2.imread(facename)
                    faces = faceCascade.detectMultiScale(
                        image, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30), flags=cv2.CASCADE_SCALE_IMAGE)
                    # print(faces)
                    (x, y, w, h) = (faces[0][0], faces[0][1],
                                    faces[0][2], faces[0][3])  # 取出第一张人脸区域
#                     print(x,y,w,h)
                    image1 = Image.open(facename).crop(
                        (x, y, x+w, y+h))  # 抓取人脸区域的图像并存至image1变量
                    # 把取得的人脸区域的分辨率变为200x200
                    image1 = image1.resize((200, 200), Image.ANTIALIAS)
                    image1.save(facename)  # 把经过处理的人脸文件保存至facename文件
                    break
        except Exception as e:
            pri(e)
            continue
    cap.release()  # 关闭摄像头
    cv2.destroyAllWindows()  # 关闭窗口
    return


def cxk(number):
    diff = 0.0
    recogname = "%s_recogface.jpg" % number  # 预存的人脸文件
    loginname = "%s_loginface.jpg" % number  # 登录者的人脸文件
    os.system("cls")  # 清屏
    if (os.path.exists(recogname)):  # 如果预存的人脸文件已存在
        msg = "摄像头打开后按 z 键进行拍照对比！"
        makeFace(loginname, msg)  # 创建登录者人脸文件
        pic1 = Image.open(recogname)  # 打开预存的人脸文件
        pic2 = Image.open(loginname)  # 打开登录者人脸文件
        h1 = pic1.histogram()  # 取预存片文件的直方图信息
        h2 = pic2.histogram()  # 取登录者图片的直方图信息
        diff = math.sqrt(reduce(operator.add, list(
            map(lambda a, b: (a-b)**2, h1, h2)))/len(h1))  # 计算两个图形差异度
    else:  # 如果预存的人脸文件不存在
        diff = 200.0
    return diff


casc_path = "D:\\codepra\\code\\.vscode\\python\\work\\scan\\using\\haarcascade_frontalface_default.xml"
faceCascade = cv2.CascadeClassifier(casc_path)  # 创建识别对象
