from ttkbootstrap import Label, Button, Frame, Entry, StringVar, Canvas, Toplevel
from tkinter.messagebox import *
import tkinter as tk
import cv2
import os
import math
import operator
from PIL import Image
from functools import reduce
from PIL import ImageTk
from time import sleep
import xlwt
from student_info_sql import *
from ScanPage import *
from funs import makeFace, cxk, pri, pri1


class LoginPage(object):
    def __init__(self, master=None):
        self.root = master
        winWidth = 650
        winHeight = 400
        screenWidth = self.root.winfo_screenwidth()
        screenHeight = self.root.winfo_screenheight()

        x = int((screenWidth - winWidth) / 2)
        y = int((screenHeight - winHeight) / 2)
        # 设置窗口初始位置在屏幕居中
        self.root.geometry("%sx%s+%s+%s" % (winWidth, winHeight, x, y))
        # 设置窗口图标
        # root.iconbitmap("./image/icon.ico")
        # 设置窗口宽高固定
        self.root.resizable(0, 0)
        self.student_number = StringVar()
        self.student_pw = StringVar()
        self.createPage()

    def createPage(self):
        '''
        登录页面
        1:创建图片组件
        2:根目录基础上添加Frame容器
        3:Frame容器上添加注册控件
        '''
        # 注释掉的背景图片，可自己打开并替换其他图片
        bm = tk.PhotoImage(file=r'logo(1).gif')
        self.lab3 = Label(self.root, image=bm)
        self.lab3.bm = bm
        self.lab3.pack()

        self.page = Frame(self.root)
        self.page.pack()
        Label(self.page).grid(row=0,)
        Label(self.page, text='    学号:   ').grid(row=1, column=0, pady=10)
        Entry(self.page, textvariable=self.student_number).grid(row=1, column=1)
        Label(self.page, text='    密码:   ').grid(row=2, column=0, pady=10)
        Entry(self.page, textvariable=self.student_pw,
              show='*').grid(row=2, column=1)
        Label(self.page, text='       ').grid(row=3, column=0, pady=10)
        Button(self.page, text='学生人脸保存注册',
               command=self.signup).grid(row=4, column=0)
        Button(self.page, text='学生人脸识别登录',
               command=self.student_loginCheck).grid(row=4, column=1)
        Label(self.page, text='       ').grid(row=5, column=0, pady=10)
        Button(self.page, text='学生帐号密码登录',
               command=self.student_loginChecknum).grid(row=6, column=1)
        Button(self.page, text='学生帐号密码注册',
               command=self.signupnum).grid(row=6, column=0)

    def student_loginCheck(self):
        global numbers, i
        '''
        学生登录
        1:获取学生学号与密码
        2:将获取到的学号与密码与数据库文件配对，配对成功返回值为正确，否则为错误
        3:将返回值判断，正确则登录界面清除，登录界面图片清除，进入用户界面，异常捕获：未填写账号或者密码
        '''
        try:
            Student_number = self.student_number.get()
            # print(User_id)
            Student_pw = self.student_pw.get()
            # print(User_pw)
            pd_student = user_slect_number_pw(Student_number, Student_pw)

            if pd_student:
                numbers = Student_number
                self.page.destroy()
                self.lab3.pack_forget()
                scanpage(self.root)

            elif i > 2:
                showinfo(title='错误', message='密码三次输入错误，此次登录被终止！')
                self.root.destroy()
            else:
                i += 1
                showinfo(title='错误', message='账号或密码错误！')
        except:
            showinfo(title='错误', message='输入错误，请重新输入！')

    def signup(self):
        Student_number = self.student_number.get()
        recogname = "%s_recogface.jpg" % Student_number
        if Student_number == "":
            showinfo(title="错误", message='请输入学生账号！')
        elif (os.path.exists(recogname)):
            showinfo(title="错误", message='该学生已保存人脸信息，可直接登录！')
        else:
            msg = "摄像头打开后按 z 键进行拍照！\n"
            makeFace(recogname, msg)  # 建立预存人脸文件
            showinfo(title='确认', message='人脸信息保存成功！')

    def signupnum(self):
        '''
        学生注册页面
        1:新建一个置于顶层的窗口
        2:将布局控件放入
        3:每个窗口的控件布局必须是一致的，place(),grid(),pack()中的一种
        '''
        def insert_sql():
            '''
            添加学生
            1:获取学生姓名，年龄，学号，密码
            2:将获取到的账号与数据库文件配对，查看是否存在相同学号，如不存在，将学生插入数据库文件，存在则提示修改账户名
            异常捕获：信息未填写
            '''
            try:

                number = self.new_number.get()

                pw = self.new_pw.get()
                if len(number) < 10:
                    showinfo(title='提示', message='学号为10位的数字，请重新输入！')
                else:
                    XWC = user_showdb(number)  # 先判断账号是否存在于学生或者教师数据库

                    if XWC == None:
                        user_insertData(number, pw)
                        showinfo(title='提示', message='注册成功')
                        self.window_sign_up.destroy()
                    else:
                        self.window_sign_up.destroy()
                        showinfo(title='提示', message='学号重复，注册失败，请修改学号！')
            except:
                self.window_sign_up.destroy()
                showinfo(title='错误', message='未知错误，请重新输入！')

        self.window_sign_up = Toplevel(self.root)
        winWidth = 300
        winHeight = 200
        self.window_sign_up.title('注册窗口')
        screenWidth = self.window_sign_up.winfo_screenwidth()
        screenHeight = self.window_sign_up.winfo_screenheight()
        x = int((screenWidth - winWidth) / 2)
        y = int((screenHeight - winHeight) / 2)
        # 设置窗口初始位置在屏幕居中
        self.window_sign_up.geometry(
            "%sx%s+%s+%s" % (winWidth, winHeight, x-50, y-50))
        # 设置窗口图标
        # root.iconbitmap("./image/icon.ico")
        # 设置窗口宽高固定
        self.window_sign_up.resizable(0, 0)

        self.new_number = StringVar()
        Label(self.window_sign_up, text='学号: ').place(x=10, y=20)
        entry_student_number = Entry(
            self.window_sign_up, textvariable=self.new_number)
        entry_student_number.place(x=130, y=20)

        self.new_pw = StringVar()
        Label(self.window_sign_up, text='密码: ').place(x=10, y=60)
        entry_usr_pw = Entry(self.window_sign_up,
                             textvariable=self.new_pw, show='*')
        entry_usr_pw.place(x=130, y=60)

        sign_up = Button(self.window_sign_up, text='注册', command=insert_sql)
        sign_up.place(x=237, y=160)

    def student_loginCheck(self):
        try:
            Student_number = self.student_number.get()
            if Student_number == "":
                showinfo(title="错误", message='请输入学生账号！')
            else:
                a = cxk(Student_number)
                if (a <= 100):  # 若差度在100内，可通过验证
                    pri("通过验证，欢迎使用本系统！ diff=%4.2f" % a)
                    self.page.destroy()
                    # 注释掉的背景图片，可自己打开并替换其他图片
                    # self.lab3.pack_forget()
                    scanpage(self.root)
                elif (a == 200.0):
                    showinfo(title='错误', message='数据库无该学生人脸信息，请先进行人脸注册！')
                else:
                    pri1("没有通过验证！ diff=%4.2f" % a)
        except Exception as e:
            print(e)
            # showinfo(title='错误',message='输入错误，请重新输入！')

    def student_loginChecknum(self):
        global numbers, i
        '''
        学生登录
        1:获取学生学号与密码
        2:将获取到的学号与密码与数据库文件配对，配对成功返回值为正确，否则为错误
        3:将返回值判断，正确则登录界面清除，登录界面图片清除，进入用户界面，异常捕获：未填写账号或者密码
        '''
        # try:
        Student_number = self.student_number.get()
        # print(User_id)
        Student_pw = self.student_pw.get()
        # print(User_pw)
        pd_student = user_slect_number_pw(Student_number, Student_pw)

        if pd_student:
            numbers = Student_number
            pri("通过验证，欢迎使用本系统！")
            self.page.destroy()
            self.lab3.pack_forget()
            scanpage(self.root)

        elif i > 2:
            showinfo(title='错误', message='密码三次输入错误，此次登录被终止！')
            self.root.destroy()
        else:
            i += 1
            showinfo(title='错误', message='账号或密码错误！')
        # except:
            #  showinfo(title='错误',message='输入错误，请重新输入！')


class MenuFrame(Frame):  # 继承Frame类
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.root = master  # 定义内部变量root
        self.createPage()

    def createPage(self):
        strs = "人脸识别登录成功！"
        Label(self.root, text=strs, font=("fangsong", 30)).pack()
        sleep(1)
        self.root.destroy()
