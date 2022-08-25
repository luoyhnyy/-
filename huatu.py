from tkinter import *
from tkinter.messagebox import *
from tkinter.filedialog import *
import tkinter.ttk as tk
from PIL import Image, ImageDraw
import tkinter.colorchooser as cc
import json
import os
import threading, time
"""
新版勾边软件 作者：AVCL系统工程中心-罗尧 2021年7月
"""
current = None
firstpoint = [] #每个勾边的第一个点
points = [] #全部勾边的点
point = [] #正在勾边的单个勾边的点
mousetype = 4 #0是未勾边模式，1是勾边模式，2是勾边完成模式,3是勾边填充完,4是桌面模式
pointtype = 0 #0是点未选中状态，1是点选中状态,2是勾边选中状态
direnum = 0 #0是上一个点，1是下一个点
px,py = 0,0 #键盘相对移动差值
cx,cy = 0,0 #鼠标相对移动差值
masknum,pointnum = 0,0 #勾边的序号和单个勾边点的序号
linew = 2 #线条宽度
backcolor = '#dddddd'
screens = [] #每个屏幕边界点列表
#w
def w_key(event):
    keymove(0)
#s
def s_key(event):
    keymove(1)
#a
def a_key(event):
    keymove(2)
#d
def d_key(event):
    keymove(3)
#wsad移动
def keymove(movenum):
    global px, py, points, current, masknum, pointnum, pointtype
    if pointtype == 1: #点选中状态
        px = points[masknum][2 * pointnum]
        py = points[masknum][2 * pointnum + 1]
        s = screens[0]
        for i in screens:
            if polygon([px,py],i):
                s = i
                break
        if movenum == 0:
            py = py - 2
        elif movenum == 1:
            py = py + 2
        elif movenum == 2:
            px = px - 2
        elif movenum == 3:
            px = px + 2
        if px == s[0][0]-1:
            px = s[0][0]
        if px == s[1][0]+1:
            px = s[1][0]
        if py == s[0][1]-1:
            py = s[0][1]
        if py == s[2][1]+1:
            py = s[2][1]
        if px < s[0][0] or px > s[1][0] or py < s[0][1] or py > s[2][1]:
            return
        drawing.delete('firstline', 'lastline', 'dbx', 'blackrect', 'red')
        points[masknum][2 * pointnum] = px
        points[masknum][2 * pointnum + 1] = py
        if mousetype == 3: #勾边填充完
            drawing.config(bg='#000000')
            for i in points:
                drawing.create_polygon(i, fill=backcolor, tag='dbx')
            fontnum()
        else:
            drawall()
        for p in range(int(len(points[masknum]) / 2)):
            drawing.create_rectangle(points[masknum][2 * p] + 5, points[masknum][2 * p + 1] + 5, points[masknum][2 * p] - 5,
                                     points[masknum][2 * p + 1] - 5, fill="white", tag='blackrect')
        drawing.create_rectangle(points[masknum][2 * pointnum] + 5, points[masknum][2 * pointnum + 1] + 5,
                                 points[masknum][2 * pointnum] - 5, points[masknum][2 * pointnum + 1] - 5, fill="red",tag='red')
    elif pointtype == 2:  # 勾边选中状态
        po = points[masknum]
        pn = int(len(po) / 2)
        s = screens[0]
        for i in screens:
            if polygon([po[0], po[1]], i):
                s = i
                break
        n = 2
        if movenum == 0: #上
            for i in range(pn):
                if po[2 * i + 1] - 2 < s[0][1]:
                    if po[2 * i + 1] - 1 < s[0][1]:
                        return
                    else:
                        n = 1
            for i in range(pn):
                points[masknum][2 * i + 1] = po[2 * i + 1] - n
        elif movenum == 1: #下
            for i in range(pn):
                if po[2 * i + 1] + 2 > s[2][1]:
                    if po[2 * i + 1] + 1 > s[2][1]:
                        return
                    else:
                        n = 1
            for i in range(pn):
                points[masknum][2 * i + 1] = po[2 * i + 1] + n
        elif movenum == 2: #左
            for i in range(pn):
                if po[2 * i] - 2 < s[0][0]:
                    if po[2 * i] - 1 < s[0][0]:
                        return
                    else:
                        n = 1
            for i in range(pn):
                points[masknum][2 * i] = po[2 * i] - n
        elif movenum == 3: #右
            for i in range(pn):
                if po[2 * i] + 2 > s[1][0]:
                    if po[2 * i] + 1 > s[1][0]:
                        return
                    else:
                        n = 1
            for i in range(pn):
                points[masknum][2 * i] = po[2 * i] + n
        drawing.delete('firstline', 'lastline', 'dbx', 'blackrect')
        if mousetype == 3:
            drawing.config(bg='#000000')
            for i in points:
                drawing.create_polygon(i, fill=backcolor, tag='dbx')
            fontnum()
        else:
            drawall()
        for p in range(int(len(points[masknum]) / 2)):
            drawing.create_rectangle(points[masknum][2 * p] + 5, points[masknum][2 * p + 1] + 5, points[masknum][2 * p] - 5,
                                     points[masknum][2 * p + 1] - 5, fill="white", tag='blackrect')
#方向键上/左
def up(event):
    global points,current,masknum,pointnum,pointtype,direnum
    direnum = 0
    direction()
#方向键下/右
def down(event):
    global points,current,masknum,pointnum,pointtype,direnum
    direnum = 1
    direction()
#方向键选择点或者勾边
def direction():
    global points, current, masknum, pointnum, pointtype
    if pointtype == 1:#and mousetype != 3: # 点选中状态,非填充完成状态
        drawing.delete('red')
        if direnum == 0:
            if pointnum != 0:
                pointnum = pointnum - 1
            else:
                pointnum = int(len(points[masknum]) / 2) - 1
        elif direnum == 1:
            if pointnum != int(len(points[masknum]) / 2) - 1:
                pointnum = pointnum + 1
            else:
                pointnum = 0
        drawing.create_rectangle(points[masknum][2 * pointnum] + 5, points[masknum][2 * pointnum + 1] + 5,
        points[masknum][2 * pointnum] - 5,points[masknum][2 * pointnum + 1] - 5, fill="red", tag='red')
    elif pointtype == 2:#and mousetype != 3:  # 勾边选中状态,非填充完成状态
        drawing.delete('blackrect')
        if direnum == 0:
            if masknum != 0:
                masknum = masknum - 1
            else:
                masknum = len(points) - 1
        elif direnum == 1:
            if masknum != len(points) - 1:
                masknum = masknum + 1
            else:
                masknum = 0
        for p in range(int(len(points[masknum]) / 2)):
            drawing.create_rectangle(points[masknum][2 * p] + 5, points[masknum][2 * p + 1] + 5,
            points[masknum][2 * p] - 5,points[masknum][2 * p + 1] - 5, fill="white", tag='blackrect')
#线条变细
def fontsmaller(event):
    global linew
    if linew != 1:
        if mousetype == 0 or mousetype == 2:
            drawing.delete('firstline', 'lastline')
            linew -= 1
            drawall()
#线条变粗
def fontbigger(event):
    global linew
    if linew != 10:
        if mousetype == 0 or mousetype == 2:
            drawing.delete('firstline', 'lastline')
            linew += 1
            drawall()
#鼠标左键点击
def leftdown(event):
    global current,point,points,px,py,masknum,pointnum,pointtype,cx,cy
    event.widget.focus_set() #焦点设置
    cx, cy = event.x, event.y
    pointtype = 0
    if mousetype == 1: #勾边模式
        # drawing.config(cursor="none")
        if current is None:
            x0 = event.x
            y0 = event.y
            firstpoint.append([x0,y0])
        else:
            coords = event.widget.coords(current)
            x0 = coords[2]
            y0 = coords[3]
            # print(x0,y0)
            # x0,y0 = point[-2], point[-1]
        if len(point) >= 2:
            for i in screens:
                if polygon([point[-2],point[-1]],i): #在多边形内
                    if event.x < i[0][0]:
                        x = i[0][0]
                    elif event.x > i[1][0]:
                        x = i[1][0]
                    else:
                        x = event.x
                    if event.y < i[0][1]:
                        y = i[0][1]
                    elif event.y > i[2][1]:
                        y = i[2][1]
                    else:
                        y = event.y
                    point.append(x0)
                    point.append(y0)
                    current = drawing.create_line(point[-2],point[-1], x, y, fill='black', width=linew, tag='firstline')
                    # current = drawing.create_line(x0, y0, x, y, fill='black', width=linew, tag='firstline')
                    break
        else:
            point.append(event.x)
            point.append(event.y)
            current = drawing.create_line(x0, y0, event.x, event.y,fill='black',width=linew,tag='firstline')
        # drawing.create_rectangle(event.x + 5, event.y + 5, event.x - 5,event.y - 5, fill="white", tag='lastline')
    elif (mousetype == 2 or mousetype == 3) and point == [] and points != []: #勾边完成状态
        drawing.config(cursor="arrow")
        drawing.delete('red','blackrect')
        n = 0 #鼠标在哪个屏内
        d = 0
        for k in range(len(screens)):
            if polygon([event.x, event.y], screens[k]):  # 在多边形内
                n = k
                break
        for i in range(len(points)):
            # if polygon([points[i][0], points[i][1]], screens[n]):
            for j in range(int(len(points[i])/2)):
                if points[i][2*j]-12<=event.x<=points[i][2*j]+12 and points[i][2*j+1]-12<=event.y<=points[i][2*j+1]+12:
                    px = points[i][2 * j]
                    py = points[i][2 * j + 1]
                    drawing.create_rectangle(points[i][2*j]+5,points[i][2*j+1]+5,points[i][2*j]-5,points[i][2*j+1]-5,fill="red",tag='red')
                    masknum, pointnum = i,j
                    pointtype = 1 #点选中状态
                    d += 1
                    break
        if d > 1:
            drawing.delete('red')
            for i in range(len(points)):
                if polygon([points[i][0], points[i][1]], screens[n]):
                    for j in range(int(len(points[i]) / 2)):
                        if points[i][2 * j] - 10 <= event.x <= points[i][2 * j] + 10 and points[i][2 * j + 1] - 10 <= event.y <= points[i][2 * j + 1] + 10:
                            px = points[i][2 * j]
                            py = points[i][2 * j + 1]
                            drawing.create_rectangle(points[i][2 * j] + 5, points[i][2 * j + 1] + 5, points[i][2 * j] - 5,points[i][2 * j + 1] - 5, fill="red", tag='red')
                            masknum, pointnum = i, j
                            break
        if pointtype != 1:
            for i in range(len(points)):
                if polygon([event.x,event.y], [[points[i][2 * k], points[i][2 * k + 1]] for k in range(int(len(points[i]) / 2))]):
                    pointtype = 2  # 勾边选中状态
                    masknum = i
                    drawing.delete('blackrect')
                    for p in range(int(len(points[i])/2)):
                        drawing.create_rectangle(points[i][2 * p] + 5, points[i][2 * p + 1] + 5, points[i][2 * p] - 5,
                                                    points[i][2 * p + 1] - 5, fill="white", tag='blackrect')
                    break
#鼠标中键
def middledown(event):
    global mousetype
    if mousetype !=3 and mousetype !=4:
        drawing.delete('red','blackrect')
        # drawing.config(cursor="none")
        # drawing.config(cursor="tcross")
        mousetype = 1 #进入勾边模式
#双击左键
def mousedouble(event):
    global current,firstpoint,point,mousetype
    event.widget.focus_set()  # 焦点设置
    if len(firstpoint) != 0 and len(point) != 2:
        # finish = askyesno("警告", "确定完成勾边？", parent=root)
        # if finish == True:
        current = drawing.create_line(point[-2],point[-1],point[0],point[1],fill='black',width=linew,tag='lastline')
        current = None
        drawing.config(cursor="arrow")
        points.append(point)
        firstpoint = []
        point = []
        mousetype = 2 #勾边完成模式
#鼠标移动
def mousemove(event):
    drawing.delete('mouse')
    if len(point) >= 2:
        for i in screens:
            if polygon([point[-2],point[-1]],i): #在多边形内
                if event.x < i[0][0]:
                    x = i[0][0]
                elif event.x > i[1][0]:
                    x = i[1][0]
                else:
                    x = event.x
                if event.y < i[0][1]:
                    y = i[0][1]
                elif event.y > i[2][1]:
                    y = i[2][1]
                else:
                    y = event.y
                break
    else:
        x,y = event.x,event.y
    if mousetype == 1:  # 勾边模式
        drawing.config(cursor="none")
        drawing.create_rectangle(x + 5, y + 5, x - 5, y - 5, fill="white", tag='mouse')
    if current:
        coords = event.widget.coords(current) # 记录上一次鼠标点下的坐标和随时移动的坐标
        coords[2] = x
        coords[3] = y
        event.widget.coords(current, *coords)
#按下ctrl+左键移动勾边
def ctrldown(event):
    global px, py, points, current, masknum, pointnum, pointtype,cx,cy
    event.widget.focus_set()
    drawing.config(cursor="fleur")
    if pointtype == 2:#and mousetype != 3:
        drawing.delete('firstline', 'lastline','blackrect','dbx')
        for i in range(int(len(points[masknum])/2)):
            points[masknum][2*i] = points[masknum][2*i] +  event.x -cx
            points[masknum][2*i+1] = points[masknum][2*i+1] + event.y -cy
        if mousetype == 3:
            drawing.config(bg='#000000')
            for i in points:
                drawing.create_polygon(i, fill=backcolor, tag='dbx')
            fontnum()
        else:
            drawall()
        cx,cy = event.x,event.y
        for p in range(int(len(points[masknum]) / 2)):
            drawing.create_rectangle(points[masknum][2 * p] + 5,points[masknum][2 * p + 1] + 5, points[masknum][2 * p] - 5,
                                            points[masknum][2 * p + 1] - 5, fill="white", tag='blackrect')
#按下ctrl+v复制勾边
def copy(event):
    global points,current, masknum, pointtype
    if pointtype == 2 and mousetype !=3 and mousetype !=4:  # 勾边选中状态
        drawing.delete('firstline', 'lastline','blackrect')
        po = points[masknum][:]
        for i in range(int(len(po) / 2)):
            po[2 * i] = po[2 * i] + 50
            po[2 * i + 1] = po[2 * i + 1] + 50
        points.append(po)
        drawall()
        for i in range(int(len(points[-1])/2)):
            drawing.create_rectangle(points[-1][2 * i] + 5, points[-1][2 * i + 1] + 5, points[-1][2 * i] - 5,
                                            points[-1][2 * i + 1] - 5, fill="white", tag='blackrect')
        masknum = -1
#撤销上一个点
def delpoint(event):
    global current, point, points, masknum, pointnum, pointtype
    event.widget.focus_set()  # 焦点设置
    pointtype = 0
    if mousetype == 1:  # 勾边模式
        drawing.delete('firstline', 'lastline')
        if len(point) > 2:
            del point[-2], point[-1]
            if len(point) == 2:
                current = drawing.create_line(point,point, fill='black', width=linew, tag='firstline')
            else:
                current = drawing.create_line(point,fill='black', width=linew, tag='firstline')
                current = drawing.create_line(point[-2],point[-1],point[-2],point[-1],fill='black', width=linew, tag='firstline')
        elif len(point) == 2:
            current = None
            point = []
        else:
            pass
        if len(points) != 0:
            drawall()
#删除指定勾边/点
def delmask(event):
    global points, current, masknum, pointtype, pointnum
    if pointtype == 2: # 勾边选中状态
        delete = askyesno("警告", "确定删除勾边？", parent=root)
        if delete == True:
            del points[masknum]
            if mousetype == 2:
                drawing.delete('firstline', 'lastline', 'red', 'blackrect')
                drawall()
            elif mousetype == 3:
                drawing.delete('firstline', 'lastline', 'dbx', 'blackrect')
                drawing.config(bg='#000000')
                for i in points:
                    drawing.create_polygon(i, fill=backcolor, tag='dbx')
                fontnum()
            pointtype = 0
    elif pointtype == 1:  # 点选中状态
        p = points[masknum]
        if len(p) >= 8:
            del p[pointnum*2]
            del p[pointnum*2]
            points[masknum] = p
        if mousetype == 2:
            drawing.delete('firstline', 'lastline', 'red', 'blackrect')
            drawall()
        elif mousetype == 3:
            drawing.delete('firstline', 'lastline','red', 'dbx', 'blackrect')
            drawing.config(bg='#000000')
            for i in points:
                drawing.create_polygon(i, fill=backcolor, tag='dbx')
            fontnum()
        pointtype = 0
#重新画所有线条
def drawall():
    for i in points:
        drawing.create_line(i, fill='black', width=linew, tag='firstline')
        drawing.create_line(i[0], i[1], i[-2], i[-1], fill='black', width=linew, tag='lastline')
#点前后插入点
def insertpoint(event):
    global points,pointtype
    if pointtype == 1:  # 点选中状态
        p = points[masknum]
        if len(p) >= 6:
            if pointnum == 0: #第一个点
                a,b = round(len(p)/2 - 1),pointnum+1 #要增加点的前后点序号
            elif pointnum == round(len(p)/2 - 1): #最后一个点
                a,b = pointnum-1,0
            else: #中间的点
                a,b = pointnum-1,pointnum+1
            x,y = p[pointnum*2],p[pointnum*2+1]
            x1,y1 = p[a*2],p[a*2+1]
            x2,y2 = p[b*2],p[b*2+1]
            c1,r1 = round((x+x1)/2),round((y+y1)/2)
            c2,r2 = round((x+x2)/2),round((y+y2)/2)
            if pointnum == 0:  # 第一个点
                p.extend([c1,r1])
                p.insert(b*2,c2)
                p.insert(b*2+1,r2)
            elif pointnum == round(len(p) / 2 - 1):  # 最后一个点
                p.insert(pointnum*2, c1)
                p.insert(pointnum*2+1, r1)
                p.extend([c2, r2])
            else: #中间的点
                p.insert(b*2, c2)
                p.insert(b*2+1, r2)
                p.insert(pointnum*2, c1)
                p.insert(pointnum*2+1, r1)
            points[masknum]=p
            if mousetype == 2:
                drawing.delete('red')
                drawing.create_rectangle(c1 + 5,r1 + 5,c1 - 5,r1 - 5, fill="white", tag='blackrect')
                drawing.create_rectangle(c2 + 5,r2 + 5,c2 - 5,r2 - 5, fill="white", tag='blackrect')
            elif mousetype == 3:
                drawing.delete('firstline', 'lastline','red', 'dbx', 'blackrect')
                drawing.config(bg='#000000')
                for i in points:
                    drawing.create_polygon(i, fill=backcolor, tag='dbx')
                fontnum()
                for p in range(int(len(points[masknum]) / 2)):
                    drawing.create_rectangle(points[masknum][2 * p] + 5, points[masknum][2 * p + 1] + 5,
                                             points[masknum][2 * p] - 5,
                                             points[masknum][2 * p + 1] - 5, fill="white", tag='blackrect')
            pointtype = 0
#按下鼠标移动点
def downmove(event):
    global px,py, points, current, masknum, pointnum, pointtype
    if pointtype == 1: #点选中状态
        # drawing.move('red', event.x - px, event.y - py)
        px,py = event.x,event.y
        s = screens[0]
        for i in screens:
            if polygon([points[masknum][2 * pointnum], points[masknum][2 * pointnum + 1]], i):
                s = i
                break
        if event.x < s[0][0]:
            px = s[0][0]
        elif event.x > s[1][0]:
            px = s[1][0]
        if event.y < s[0][1]:
            py = s[0][1]
        elif event.y > s[2][1]:
            py = s[2][1]
        points[masknum][2 * pointnum] = px
        points[masknum][2 * pointnum + 1] = py
        drawing.delete('firstline', 'lastline', 'blackrect', 'dbx', 'red')
        if mousetype == 3:
            drawing.config(bg='#000000')
            for i in points:
                drawing.create_polygon(i, fill=backcolor, tag='dbx')
            fontnum()
        else:
            drawall()
        for p in range(int(len(points[masknum]) / 2)):
            drawing.create_rectangle(points[masknum][2 * p] + 5, points[masknum][2 * p + 1] + 5, points[masknum][2 * p] - 5,
                                     points[masknum][2 * p + 1] - 5, fill="white", tag='blackrect')
        drawing.create_rectangle(points[masknum][2 * pointnum] + 5, points[masknum][2 * pointnum + 1] + 5,
                                 points[masknum][2 * pointnum] - 5, points[masknum][2 * pointnum + 1] - 5, fill="red",
                                 tag='red')
#按下空格，填充/取消填充轮廓
def fillmask(event):
    global points,mousetype,pointtype,backcolor
    pointtype =0
    if mousetype == 2 or mousetype == 4:
        drawing.config(cursor="arrow")
        drawing.delete("all")
        if len(points) == 0:
            for i in screens:
                point = []
                for j in i:
                    point.append(j[0])
                    point.append(j[1])
                points.append(point)
        else:
            a = []
            for i in range(len(screens)):
                for j in points:
                    if polygon([j[0],j[1]],screens[i]):
                        a.append(i) #屏幕内有点
                        break
            for i in range(len(screens)):
                if i not in a:
                    p = []
                    for j in screens[i]:
                        p.append(j[0])
                        p.append(j[1])
                    points.append(p)
        for i in points:
            drawing.create_polygon(i, fill=backcolor,tag='dbx')
        mousetype = 3 #填充完成
        drawing.config(bg='#000000')
        fontnum()
    elif mousetype == 3:
        drawing.config(cursor="arrow")
        drawing.delete('dbx')
        drawing.config(bg=backcolor)
        drawall()
        fontnum()
        mousetype = 2 #勾边完成
#点，多边形
def polygon(e,poly):
    sinsc = 0  # 交点个数
    if len(poly) == 2: #一条直线
        if abs((poly[0][1]-poly[1][1])/(poly[0][0]-poly[1][0])) <= 1:
            if poly[0][0] < poly[1][0]:
                A = [poly[0][0] - 5, poly[0][1] - 5]
                B = [poly[0][0] - 5, poly[0][1] + 5]
                C = [poly[1][0] + 5, poly[1][1] + 5]
                D = [poly[1][0] + 5, poly[1][1] - 5]
            else:
                A = [poly[1][0] - 5, poly[1][1] - 5]
                B = [poly[1][0] - 5, poly[1][1] + 5]
                C = [poly[0][0] + 5, poly[0][1] + 5]
                D = [poly[0][0] + 5, poly[0][1] - 5]
        else:
            if poly[0][1] < poly[1][1]:
                A = [poly[0][0] - 5, poly[0][1] - 5]
                B = [poly[0][0] + 5, poly[0][1] - 5]
                C = [poly[1][0] + 5, poly[1][1] + 5]
                D = [poly[1][0] - 5, poly[1][1] + 5]
            else:
                A = [poly[1][0] - 5, poly[1][1] - 5]
                B = [poly[1][0] + 5, poly[1][1] - 5]
                C = [poly[0][0] + 5, poly[0][1] + 5]
                D = [poly[0][0] - 5, poly[0][1] + 5]
        a = (B[0] - A[0]) * (e[1] - A[1]) - (B[1] - A[1]) * (e[0] - A[0])
        b = (C[0] - B[0]) * (e[1] - B[1]) - (C[1] - B[1]) * (e[0] - B[0])
        c = (D[0] - C[0]) * (e[1] - C[1]) - (D[1] - C[1]) * (e[0] - C[0])
        d = (A[0] - D[0]) * (e[1] - D[1]) - (A[1] - D[1]) * (e[0] - D[0])
        if (a > 0 and b > 0 and c > 0 and d > 0) or (a < 0 and b < 0 and c < 0 and d < 0):
            sinsc = 1
    elif len(poly) == 3: #三角形
        for i in range(len(poly)):
            a = poly[i]
            if i < (len(poly)-1):
                b = poly[i+1]
                c = poly[i-1]
            else:
                b = poly[0]
                c = poly[i-1]
            if a[0]==b[0]==c[0] or a[1]==b[1]==c[1]: #一条支线或一个点，重叠
                continue
            if e[1] == a[1] and a[1] == b[1]:  # 重叠
                continue
            if e[1] == a[1] and a[1] == c[1]:  # 重叠
                continue
            if e[1] == b[1] and b[1] == c[1]:  # 重叠
                continue
            elif e[1] < a[1] and e[1] < b[1]:  # 线段在射线上边
                continue
            elif e[1] > a[1] and e[1] > b[1]:  # 线段在射线下边
                continue
            elif e[0] > a[0] and e[0] > b[0]:  # 线段在射线左边
                continue
            elif e[1]==a[1]: #端点相交
                if (a[1]-b[1])*(a[1]-c[1]) < 0:
                    sinsc += 1
                    continue
            else:
                xseg = b[0] - (b[0] - a[0]) * (b[1] - e[1]) / (b[1] - a[1])  # 求交
                if xseg <= e[0]:  # 交点在射线起点的左侧或在边线上
                    continue
                else:
                    sinsc += 1  # 排除上述情况之后
    elif len(poly) > 3:
        if len(poly) == 4: #4个点
            for i in range(len(poly)):
                if i == 3:
                    a,b = poly[3],poly[0]
                else:
                    a,b = poly[i],poly[i+1]
                if a[0] == b[0]:
                    if e[0] == a[0] and (b[1] >= e[1] >= a[1] or b[1] <= e[1] <= a[1]):
                        return True
                if a[1] == b[1]:
                    if e[1] == a[1] and (b[0] >= e[0] >= a[0] or b[0] <= e[0] <= a[0]):
                        return True
        for i in range(len(poly)):
            a = poly[i]
            d = poly[i-1]
            c = poly[i-2]
            if i == (len(poly)-1):
                b = poly[0]
            else:
                b = poly[i + 1]
            if e[1] != a[1] and a[1] == b[1]:  # 平行
                continue
            elif (e[1] < a[1]) and (e[1] < b[1]):  # 线段在射线上边
                continue
            elif (e[1] > a[1]) and (e[1] > b[1]):  # 线段在射线下边
                continue
            elif (e[0] > a[0]) and (e[0] > b[0]):  # 线段在射线左边
                continue
            elif e[1] == b[1] and e[1] != a[1]: # 下端点相交
                continue
            elif e[1] == a[1]:  # 端点相交
                if a[1] == b[1]: #重叠
                    continue
                elif a[1] == d[1]:
                    if (a[1] - b[1]) * (a[1] - c[1]) > 0:
                        continue
                    elif (a[1] - b[1]) * (a[1] - c[1]) < 0:
                        sinsc += 1
                        continue
                elif (a[1] - b[1]) * (a[1] - d[1]) > 0:
                    continue
                elif (a[1] - b[1]) * (a[1] - d[1]) < 0:
                    sinsc += 1
                    continue
            else:
                xseg = b[0] - (b[0] - a[0]) * (b[1] - e[1]) / (b[1] - a[1])  # 求交
                if xseg <= e[0]:  # 交点在射线起点的左侧或在边线上
                    continue
                elif xseg > e[0]:
                    sinsc += 1  # 排除上述情况之后
    return True if sinsc % 2 == 1 else False
#清除屏幕所有勾边
def clearscreen(event):
    global current, firstpoint, points, point, mousetype, pointtype, px, py, masknum, pointnum, image_mb, draw
    if mousetype != 1:
        clear = askyesno("警告", "确定清空屏幕勾边？",parent=root)
        if clear == True:
            drawing.delete('all')
            current = None
            fontnum()
            firstpoint = []  # 每个勾边的第一个点
            points = []  # 全部勾边的点
            point = []  # 单个勾边的点
            mousetype = 0  # 0是未勾边模式，1是勾边模式，2是勾边完成模式,3是勾边填充完,4是桌面模式
            pointtype = 0  # 0是点未选中状态，1是点选中状态,2是勾边选中状态
            px, py = 0, 0
            masknum, pointnum = 0, 0  # 勾边的序号和单个勾边点的序号
            image_mb = Image.new("RGB", (root.winfo_screenwidth(), root.winfo_screenheight()), (0, 0, 0))
            draw = ImageDraw.Draw(image_mb)
            drawing.config(bg=backcolor)
#右键
def rightdown(event):
    global mousetype,point
    if mousetype != 1:
        menu = Menu(drawing, tearoff=False)  # 创建一个菜单
        if mousetype == 4:
            menu.add_command(label='切换勾边模式    Enter', command=lambda: transparent(event))
        else:
            menu.add_command(label='切换蒙版模式    Enter', command=lambda: transparent(event))
        if mousetype !=3:
            menu.add_command(label='填充轮廓        Space', command=lambda: fillmask(event))
        else:
            menu.add_command(label='取消填充        Space', command=lambda: fillmask(event))
        if mousetype != 4 and mousetype !=3:
            menu.add_command(label='新建勾边       Middle', command=lambda: middledown(event))
        if pointtype == 2: #勾边选中
            menu.add_command(label='删除勾边        Delete', command=lambda: delmask(event))
        elif pointtype == 1: #点选中
            menu.add_command(label='删除点          Delete', command=lambda: delmask(event))
            menu.add_command(label='增加点          Insert', command=lambda: insertpoint(event))
        if mousetype != 4 and mousetype != 3:
            if pointtype == 2:  # 勾边选中
                menu.add_command(label='粘贴              Ctrl+V', command=lambda: copy(event))
            menu.add_command(label='跨屏方式（%s*%s）'%(srch.get(),srcw.get()), command=lambda: selectkuap())
            menu.add_command(label='背景颜色        Ctrl+E', command=lambda: choosecolor(event))
        menu.add_command(label='清屏                  Tab', command=lambda: clearscreen(event))
        menu.add_command(label='全屏              Ctrl+W', command=lambda: toggle_fullscreen(event))
        menu.add_command(label='退出全屏        Ctrl+Q', command=lambda: end_fullscreen(event))
        menu.add_command(label='关于              Ctrl+H', command=lambda: about(event))
        menu.add_command(label='保存项目        Ctrl+D', command=lambda: savejson(event))
        menu.add_command(label='读取项目        Ctrl+F', command=lambda: openjson(event))
        menu.add_command(label='保存蒙版        Ctrl+S', command=lambda: savemask(event))
        menu.add_command(label='退出                  Esc', command=lambda: quit(event))
        menu.post(event.x_root, event.y_root)
    else:
        menu = Menu(drawing, tearoff=False)  # 创建一个菜单
        if len(point) == 0:
            menu.add_command(label='取消',command=lambda:cancelmask(event))
        else:
            menu.add_command(label='撤销上个点     Ctrl+Z',command=lambda:delpoint(event))
            menu.add_command(label='保存项目        Ctrl+D', command=lambda: savejson(event))
        menu.post(event.x_root, event.y_root)
#取消勾边
def cancelmask(event):
    global points,mousetype
    drawing.config(cursor="arrow")
    if len(points) == 0:
        mousetype = 0
    else:
        mousetype = 2
#保存蒙版文件
def savemask(event):
    global mousetype,points,draw,image_mb
    image_mb = Image.new("RGB", (root.winfo_screenwidth(), root.winfo_screenheight()), (0, 0, 0))
    draw = ImageDraw.Draw(image_mb)
    if mousetype == 3 or mousetype == 4 or mousetype == 2:
        for i in points:
            draw.polygon(i, fill='white')
    # elif mousetype == 2:
    #     for i in points:
    #         draw.line(i,fill='white')
    #         draw.line([i[0], i[1], i[-2], i[-1]], fill='white')
    if mousetype != 1:
        image_mb.save("mb.png")
        showinfo("保存提示", "保存蒙版成功!", parent=root)
    elif mousetype == 1:
        showinfo("保存提示", "正在勾边，不能保存!", parent=root)
#保存项目
def savejson(event):
    global mousetype,point,points
    pb = points[:]
    pb.insert(0, mousetype)
    if len(point) > 0:
        pb.append(point)
    jsonname = 'mb.json'
    with open(jsonname, 'w') as jsons:
        json.dump(pb, jsons)
    showinfo("保存提示", "保存项目文件成功",parent=root)
#打开项目
def openjson(event):
    global current, firstpoint, point, points, mousetype, pointtype, px, py, masknum, pointnum, image_mb, draw, backcolor
    if mousetype != 1:
        jsonfile = askopenfilename(title='选择项目文件', filetype=[("项目文件", "*.json")])
        if os.path.exists(jsonfile):
            jsonf = open(jsonfile, 'r')
            with jsonf as jsons:
                pb = json.load(jsons)
            jsonf.close()
            drawing.delete('all')
            current = None
            fontnum()
            drawing.config(bg=backcolor)
            mousetype = 2  # 0是未勾边模式，1是勾边模式，2是勾边完成模式,3是勾边填充完,4是桌面模式
            pointtype = 0  # 0是点未选中状态，1是点选中状态,2是勾边选中状态
            firstpoint = []  # 每个勾边的第一个点
            px, py = 0, 0
            masknum, pointnum = 0, 0  # 勾边的序号和单个勾边点的序号
            image_mb = Image.new("RGB", (wid, hei), (0, 0, 0))
            draw = ImageDraw.Draw(image_mb)
            if pb[0] != 1:
                point = []
                points = pb[1:]
                drawall()
            else:
                points = pb[1:]
                mousetype = 1
                for i in points:
                    if len(i) != 2:
                        drawing.create_line(i, fill='black', width=linew, tag='firstline')
                    if i != points[-1]:
                        drawing.create_line(i[0], i[1], i[-2], i[-1], fill='black', width=linew, tag='lastline')
                    else:
                        point = i
                        event.widget.focus_set()  # 焦点设置
                        firstpoint.append([i[0], i[1]])
                        current = drawing.create_line(point[-2], point[-1], event.x, event.y, fill='black', width=linew, tag='firstline')
                if len(points) > 0:
                    del points[-1]
    else:
        showinfo("提示", "当前勾边未完成不能读取！", parent=root)
#关于
def about(event):
    showinfo("关于", "华强方特（深圳）智能技术有限公司\nAVCL系统工程中心\t2021年7月\n(按住Ctrl+选中勾边,可以鼠标拖动.\n"
                   "wsad,↑↓←→可移动勾边和点\nF1 F2可更改线条粗细)", parent=root)
#退出
def quit(event):
    close = askyesno("退出提示","确定退出？",parent=root)
    if close == True:
        # root.quit()
        root.destroy()
#全屏
def toggle_fullscreen(event):
    root.attributes("-fullscreen", True)
#取消全屏
def end_fullscreen(event):
    root.attributes("-fullscreen", False)
#更改背景颜色
def choosecolor(event):
    global backcolor
    if mousetype != 4 and mousetype != 3:
        choose = cc.askcolor(color='#dddddd', parent=root)
        backcolor = choose[1]
        drawing.config(bg=backcolor)
#屏幕中间加数字
def fontnum():
    global screens
    screens = []
    drawing.delete('font')
    w,h = round(wid/srcw.get()),round(hei/srch.get())
    for j in range(srch.get()):
        for i in range(srcw.get()):
            drawing.create_text(int(i*w+w/2),int(j*h+h/2),text=str(j*srcw.get()+i),font=('宋体', 50),fill='red', tag='font')
            screens.append([[w*i,h*j], [w*(i + 1) - 1, h * j], [w * (i + 1) - 1, h * (j + 1) - 1],[w * i, h * (j + 1) - 1]])
    # print(screens)
#第一次屏幕中间加数字
def firstfontnum():
    global screens
    screens = []
    if wid % 1920 == 0 and hei % 1200 == 0:
        srcw.set(int(wid/1920))
        srch.set(int(hei/1200))
        for j in range(srch.get()):
            for i in range(srcw.get()):
                drawing.create_text(i*1920+960,j*1200+600, text=str(j*srcw.get()+i), font=('宋体', 50), fill='red',tag='font')
                screens.append([[1920*i,1200*j],[1920*(i+1)-1,1200*j],[1920*(i+1)-1,1200*(j+1)-1],[1920*i,1200*(j+1)-1]])
    elif wid % 4096 == 0 and hei % 2160 == 0:
        srcw.set(int(wid / 4096))
        srch.set(int(hei / 2160))
        for j in range(srch.get()):
            for i in range(srcw.get()):
                drawing.create_text(i*4096+2048,j*2160+1080, text=str(j*srcw.get()+i), font=('宋体', 50), fill='red',tag='font')
                screens.append([[4096*i,2160*j],[4096*(i+1)-1,2160*j],[4096*(i+1)-1,2160*(j+1)-1],[4096*i,2160*(j+1)-1]])
    elif wid % 1280 == 0 and hei % 800 == 0:
        srcw.set(int(wid / 1280))
        srch.set(int(hei / 800))
        for j in range(srch.get()):
            for i in range(srcw.get()):
                drawing.create_text(i*1280+640,j*800+400, text=str(j*srcw.get()+i), font=('宋体', 50), fill='red',tag='font')
                screens.append([[1280*i,800*j],[1280*(i+1)-1,800*j],[1280*(i+1)-1,800*(j+1)-1],[1280*i,800*(j+1)-1]])
    else:
        srcw.set(1)
        srch.set(1)
        drawing.create_text(wid/2, hei/2,text='0',font=('宋体',50),fill='red',tag='font')
        screens.append([[0,0],[wid-1,0],[wid-1,hei-1],[0,hei-1]])
#选择跨屏
def selectkuap():
    global top,cob1,cob2
    def quittop():
        top.destroy()
        top.quit()
        kpopen.set(False)

    if kpopen.get():
        quittop()
    kpopen.set(True)
    top = Toplevel()
    top.title("选择跨屏方式")
    top.geometry('240x60')
    top.wm_attributes('-topmost', 1)  # 置顶
    Label(top,text="行").place(width=120,height=30,x=0,y=0)
    cob1 = tk.Combobox(top, values=[i for i in range(1,9)], textvariable=srch)
    cob1.bind("<<ComboboxSelected>>", kuap)
    cob1.place(width=120,height=30,x=120,y=0)
    Label(top, text="列").place(width=120, height=30, x=0, y=30)
    cob2 = tk.Combobox(top, values=[i for i in range(1, 9)], textvariable=srcw)
    cob2.bind("<<ComboboxSelected>>", kuap)
    cob2.place(width=120, height=30, x=120, y=30)
    top.protocol('WM_DELETE_WINDOW', quittop)
    top.mainloop()
def kuap(a):
    if srch.get() == 1:
        cob2['values'] = [i for i in range(1, 9)]
    elif srch.get() == 2:
        cob2['values'] = [i for i in range(1, 5)]
    elif srch.get() == 3 or srch.get() == 4:
        cob2['values'] = [i for i in range(1, 3)]
    elif 5<= srch.get() <= 8:
        cob2['values'] = [1]
    if srcw.get() == 1:
        cob1['values'] = [i for i in range(1, 9)]
    elif srcw.get() == 2:
        cob1['values'] = [i for i in range(1, 5)]
    elif srcw.get() == 3 or srcw.get() == 4:
        cob1['values'] = [i for i in range(1, 3)]
    elif 5<= srcw.get() <= 8:
        cob1['values'] = [1]
    fontnum()
#切换勾边/蒙版模式
def transparent(event):
    global mousetype,points
    if mousetype != 1 and mousetype == 4:
        mousetype = 2 #勾边完成模式
        drawing.config(bg=backcolor)
        drawing.delete('all')
        fontnum()
        drawall()
    elif mousetype != 1 and mousetype != 4:
        mousetype = 4 #桌面模式
        drawing.delete('all')
        drawing.config(bg='black')
        # print(points)
        if len(points) == 0:
            for i in screens:
                point = []
                for j in i:
                    point.append(j[0])
                    point.append(j[1])
                points.append(point)
        else:
            a = []
            for i in range(len(screens)):
                for j in points:
                    if polygon([j[0],j[1]],screens[i]):
                        a.append(i) #屏幕内有点
                        break
            for i in range(len(screens)):
                if i not in a:
                    p = []
                    for j in screens[i]:
                        p.append(j[0])
                        p.append(j[1])
                    points.append(p)
        # for i in points:
        #     for j in range(int(len(i)/2)):
        #         print(i[2*j],i[2*j+1])
        for i in points:
            drawing.create_polygon(i, fill='gray', tag='desktop')

root = Tk()
root.attributes("-fullscreen", True) #全屏，False取消全屏
wid = root.winfo_screenwidth()
hei = root.winfo_screenheight()
srcw = IntVar() #竖向列
srcw.set(1)
srch = IntVar() #横向行
srch.set(1)
kpopen = BooleanVar() #跨屏选择是否打开
kpopen.set(False)
root.geometry("%dx%d" % (wid, hei))
root.wm_attributes('-topmost',1) #置顶
# root.geometry("%dx%d" % (1000, 600))
drawing = Canvas(root,width=wid, height=hei, bg='black',highlightthickness=0)
drawing.pack()
# 软件刚打开
def begin(event):
    global drawing,mousetype,point,points,current,backcolor
    drawing.unbind("<Enter>")
    if os.path.exists('mb.json'):
        mb = open('mb.json', 'r')
        with mb as jsons:
            pb = json.load(jsons)
        mb.close()
        if len(pb) == 1:
            mousetype = 4
            root.wm_attributes("-transparentcolor", 'gray')
            drawing.create_oval(wid / 2 - 150, hei / 2 - 150, wid / 2 + 150, hei / 2 + 150, fill='gray', tag='desktop')
        else:
            root.wm_attributes("-transparentcolor", 'gray')
            if int(pb[0]) != 1:
                mousetype = 4
                drawing.config(bg='black')
                points = pb[1:]
                for i in points:
                    drawing.create_polygon(i, fill='gray', tag='desktop')
            else:
                mousetype = 1
                drawing.config(bg=backcolor)
                firstfontnum()
                points = pb[1:]
                for i in points:
                    if len(i) != 2:
                        drawing.create_line(i, fill='black', width=linew, tag='firstline')
                    if i != points[-1]:
                        drawing.create_line(i[0], i[1], i[-2], i[-1], fill='black', width=linew, tag='lastline')
                    else:
                        point = i
                        event.widget.focus_set()  # 焦点设置
                        firstpoint.append([i[0], i[1]])
                        current = drawing.create_line(point[-2], point[-1], event.x, event.y, fill='black', width=linew,
                                                      tag='firstline')
                if len(points) > 0:
                    del points[-1]
    else:
        root.wm_attributes("-transparentcolor", 'gray')
        drawing.create_oval(wid/2-150,hei/2-150,wid/2+150,hei/2+150, fill='gray', tag='desktop')

drawing.bind("<Enter>",begin)
image_mb = Image.new('RGB', (wid, hei), (0, 0, 0))
draw = ImageDraw.Draw(image_mb)
drawing.bind("<w>", w_key)  # W
drawing.bind("<s>", s_key)  # S
drawing.bind("<a>", a_key)  # A
drawing.bind("<d>", d_key)  # D
drawing.bind("<Up>", up)  # 上
drawing.bind("<Down>", down)  # 下
drawing.bind("<Left>", up)  # 左
drawing.bind("<Right>", down)  # 右
drawing.bind("<F1>", fontsmaller)  # F1
drawing.bind("<F2>", fontbigger)  #F2
drawing.bind("<Motion>", mousemove) #鼠标移动
drawing.bind("<Button-1>", leftdown) #鼠标左键点点击
drawing.bind("<Button-2>", middledown) #鼠标中键点点击
drawing.bind("<Button-3>", rightdown) #鼠标右键点点击
drawing.bind("<space>", fillmask) #点击空格键填充/取消填充轮廓
drawing.bind("<Return>", transparent) #点击回车键
drawing.bind("<Tab>", clearscreen) #点击Tab键
drawing.bind("<Escape>", quit) #点击Esc键
drawing.bind("<Control-B1-Motion>", ctrldown) #按下鼠标左键和Ctri键移动
drawing.bind("<Delete>", delmask) #按下删除键
drawing.bind("<Insert>", insertpoint) #按下插入键
drawing.bind("<Control-z>", delpoint) #按下Ctrl+z撤销
drawing.bind("<Control-e>", choosecolor) #按下Ctrl+e更改背景颜色
drawing.bind("<Control-v>", copy) #按下Ctrl+v复制单个勾边
drawing.bind("<Control-s>", savemask) #按下Ctrl+s保存勾边文件
drawing.bind("<Control-d>", savejson) #按下Ctrl+d保存项目文件
drawing.bind("<Control-f>", openjson) #按下Ctrl+f读取项目文件
drawing.bind("<B1-Motion>", downmove) #按下鼠标左键移动
drawing.bind("<Double-Button-1>", mousedouble) #鼠标左键双击
drawing.bind("<Control-w>", toggle_fullscreen)  # 按Alt+w切换全屏
drawing.bind("<Control-q>", end_fullscreen) #按Alt+q退出全屏
drawing.bind("<Control-h>", about) #按Alt+h关于
k = 0
#保存临时项目
def excep():
    global k
    while k == 0:
        time.sleep(30)  # 30秒保存一次
        mbs = open(r'临时.json', 'w')
        pb = points[:]
        pb.insert(0,mousetype)
        if len(point) > 0:
            pb.append(point)
        with mbs as jsons:
            json.dump(pb, jsons)
        mbs.close()

save_excep = threading.Thread(target = excep)
save_excep.setDaemon(True)
save_excep.start()
root.mainloop()
k += 1
# save_excep.join()