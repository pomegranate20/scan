from tkinter.messagebox import *
from tkinter import *
from login import *  # 菜单栏对应的各个子页面

root = Tk()  # 建立一个根窗口，所有窗口的基础
root.title('扫描全能王')
LoginPage(root)  # 进入调用登录
root.mainloop()
