from tkinter import Tk
from ttkbootstrap import StringVar, Frame
from time import strftime
from ttkbootstrap import Label, Button
from ttkbootstrap import Style, Canvas
from ttkbootstrap import font, CENTER
from PIL import ImageTk, Image
from login import *
from funs import gray, rec, judge


class scanpage:
    def __init__(self, window):
        self.window = window
        self.window.title("扫描全能王")
        self.window.geometry("300x270")
        self.window.resizable(0, 0)  # 窗体大小不允许变，两个参数分别代表x轴和y轴
        self.frame = Frame(self.window)
        self.frame.pack()
        self.label()
        self.clock()

    def label(self):
        # 一些装饰性工作
        self.style = Style()
        self.style = Style(theme='morph')
        font1 = font.Font(family='汉仪颜楷W', size=15)  # 字体
        font2 = font.Font(size=9)

        Label(self.frame, text=' ', font=font2).place(relx=0.73, rely=0.45, relheight=0.04,
                                                      relwidth=0.1)

        canvas_root = Canvas(self.frame, width=300, height=60)
        img = Image.open(
            "logo.png").resize((270, 60))
        photo = ImageTk.PhotoImage(img)
        canvas_root.create_image(150, 30, image=photo)
        # GUI
        Label(self.frame, text='欢迎您使用扫描全能王',
              font=font1, compound=CENTER).pack()

        Label(self.frame, text=' ', font=font2).pack()

        Label(self.frame, text=' ', font=font2).pack()

        Button(self.frame, text="文件扫描", command=gray).pack()

        Label(self.frame, text=' ', font=font2).pack()

        Button(self.frame, text='答题卡判卷', command=judge).pack()

        Label(self.frame, text=' ', font=font2).pack()

        Button(self.frame, text='图片文字识别', command=rec).pack()

        Label(self.frame, text=' ', font=font2).pack()

        Label(self.frame, text='By LiuNuohong', font=font2).pack()

    def clock(self):
        # 获取时间的函数
        def gettime():
            # 获取当前时间
            dstr.set(strftime("%H:%M:%S"))
            # 每隔 1s 调用一次 gettime()函数来获取时间
            self.frame.after(1000, gettime)

        # 生成动态字符串
        dstr = StringVar()
        # 利用 textvariable 来实现文本变化
        Label(self.frame, textvariable=dstr, foreground='#4169E1', font=("微软雅黑", 10)).place(relx=0.35, rely=0.14,
                                                                                            relheight=0.12,
                                                                                            relwidth=0.3)

        # 调用生成时间的函数
        gettime()
