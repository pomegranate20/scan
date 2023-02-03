# -*- coding:utf-8 -*-
import sqlite3
# 打开学生数据库


def user_opendb():
    conn = sqlite3.connect("student.db")
    cur = conn.execute("""create table if not exists student_info(
        id integer PRIMARY KEY autoincrement,
        student_number varchar(10),
        student_passworld varchar(128))""")
    return cur, conn

# 查询所有列名


def user_lie_name():
    hel = user_opendb()
    cur = hel[1].cursor()
    cur.execute("select * from student_info")
    col_name_list = [tuple[0] for tuple in cur.description]
    return col_name_list
    cur.close()

# 查询学生全部信息


def user_slectTable():
    hel = user_opendb()
    cur = hel[1].cursor()
    cur.execute("select * from student_info")
    res = cur.fetchall()
    # for line in res:
    # for h in line:
    # print(h),
    # print(line)
    return res
    cur.close()
#  往学生数据库中添加内容


def user_insertData(number, pw):

    hel = user_opendb()
    hel[1].execute(
        "insert into student_info(student_number, student_passworld)values (?,?)", (number, pw))
    hel[1].commit()
    hel[1].close()
# 查询学生个人信息


def user_showdb(number):
    hel = user_opendb()
    cur = hel[1].cursor()
    cur.execute("select * from student_info where student_number="+number)
    res = cur.fetchone()
    cur.close()
    return res

#   删除学生数据库中的指定内容


def user_deldb(number):

    hel = user_opendb()              # 返回游标conn
    hel[1].execute("delete from student_info where student_number="+number)
    print("已删除学号为 %s 学生" % number)
    hel[1].commit()
    hel[1].close()

#  修改学生数据库的内容


def user_alter(number, pw):
    hel = user_opendb()
    hel[1].execute(
        "update student_info set student_passworld= ? where student_number="+number, (pw))
    hel[1].commit()
    hel[1].close()

#  修改学生数据库密码的内容


def user_alter_pw(number, pw):
    hel = user_opendb()
    hel[1].execute(
        "update student_info set student_passworld= %s where student_number=%s" % (pw, number))
    hel[1].commit()
    hel[1].close()

# 登录查询学生数据


def user_slect_number_pw(number, pw):
    hel = user_opendb()
    cur = hel[1].cursor()
    cur.execute("select * from student_info where student_number=" +
                number+" and student_passworld= "+pw)
    hel[1].commit()
    for row in cur:
        if row:
            return True
        else:
            return False
    cur.close()
    hel[1].close()
