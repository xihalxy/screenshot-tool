import pyautogui
import os
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
from io import BytesIO
import win32clipboard
import time
import xml.dom.minidom
class tools():
    def __init__(self):
        self.parse_config()
        self.cvs=[]
        self.root = tk.Tk()
        self.root.geometry("290x60")
        self.root.iconbitmap("icon.ico")
        self.root.title("截图工具")
        new_screen_Btn = tk.Button(self.root, text ="新建截图", command = lambda:self.newscreen(None))
        new_screen_Btn.place(x=10,y=10,width=90,height=40)
        save_model_Btn = tk.Button(self.root, text ="保存项目", command = lambda:self.save_model(None))
        save_model_Btn.place(x=100,y=10,width=90,height=40)
        load_model_Btn = tk.Button(self.root, text ="导入项目", command = lambda:self.load_model(None))
        load_model_Btn.place(x=190,y=10,width=90,height=40)
        self.root.bind("<"+self.control.getElementsByTagName("newscreenshot")[0].firstChild.data+">",self.newscreen)
        self.root.bind("<"+self.control.getElementsByTagName("savemodel")[0].firstChild.data+">",self.save_model)
        self.root.bind("<"+self.control.getElementsByTagName("loadmodel")[0].firstChild.data+">",self.load_model)
        self.root.mainloop()
    def parse_config(self):
        dom = xml.dom.minidom.parse('config.xml')
        root = dom.documentElement
        self.path=dom.getElementsByTagName("picture")[0].firstChild.data
        self.modelpath = dom.getElementsByTagName("model")[0].firstChild.data
        self.control = dom.getElementsByTagName("control")[0]
    #创建截屏主界面
    def newscreen(self,event):
        self.screenshot = tk.Toplevel()
        self.screenshot.overrideredirect(True)         # 隐藏窗口的标题栏
        self.screenshot.attributes("-alpha", 0.1)      # 窗口透明度10%
        self.screenshot.geometry("{0}x{1}+0+0".format(self.root.winfo_screenwidth(), self.root.winfo_screenheight()))
        self.screenshot.configure(bg="black")
        self.screenshot.bind("<"+self.control.getElementsByTagName("exitscreenshot")[0].firstChild.data+">",self.shot_out)
        self.screenshot.bind("<Button-1>", self.button_1)  # 鼠标左键点击->显示子窗口 
        self.screenshot.bind("<B1-Motion>", self.b1_Motion)# 鼠标左键移动->改变子窗口大小
        self.screenshot.bind("<ButtonRelease-1>", self.buttonRelease_1) # 鼠标左键释放->记录最后光标的位置
        self.screenshot.bind("<"+self.control.getElementsByTagName("hungshot")[0].firstChild.data+">",self.button_3)

        # 再创建1个Canvas用于圈选
        self.cv = tk.Canvas(self.screenshot)
        self.x, self.y = 0, 0
        self.xstart,self.ystart = 0 ,0
        self.xend,self.yend = 0, 0
        self.rec = ''  
        self.screenshot.mainloop()  
    #创建子窗口
    def button_1(self,event):
        self.cv.delete(self.rec)
        self.cv.place_forget()
        self.x, self.y = event.x, event.y
        self.xstart,self.ystart = event.x, event.y
        self.cv.configure(height=1)
        self.cv.configure(width=1)
        self.cv.config(highlightthickness=0) # 无边框
        self.cv.place(x=event.x, y=event.y)
        self.rec = self.cv.create_rectangle(0,0,0,0,outline='red',width=8,dash=(4, 4))
            
    #改变子窗口大小
    def b1_Motion(self,event):
        self.x, self.y = event.x, event.y
        height = event.y - self.ystart if event.y>self.ystart else self.ystart-event.y
        if event.y<self.ystart:
            self.cv.place(y=event.y)
        width = event.x - self.xstart if event.x>self.xstart else self.xstart-event.x
        if(event.x<self.xstart):
            self.cv.place(x=event.x)
        self.cv.configure(height = height)
        self.cv.configure(width = width)
        self.cv.coords(self.rec,0,0,width,height)
    #记录松开鼠标位置
    def buttonRelease_1(self,event):
        self.xend, self.yend = event.x, event.y
    
    #截图并保存
    def button_3(self,event):
        self.cv.delete(self.rec)
        self.cv.place_forget()
        if(self.xstart>self.xend):
            self.xstart,self.xend=self.xend,self.xstart
        if(self.ystart>self.yend):
            self.ystart,self.yend=self.yend,self.ystart
        img = pyautogui.screenshot(region=[self.xstart,self.ystart,self.xend-self.xstart,self.yend-self.ystart]) # x,y,w,h
        self.cvs.append(self.image_show(img,self.path,self.root,self.control))
        self.shot_out(None)
    def shot_out(self,even):
        self.screenshot.destroy()
    def save_model(self,event):
        path = self.modelpath+"/model/"+time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())
        folder = os.path.exists(path)
        if not folder:
            os.makedirs(path)
        with open(path+"/location.shot","w") as f:
            for i in range(len(self.cvs)):
                item = self.cvs[i].__dict__
                if(item.get("image")!=None):
                    line = str(i)+" "+str(item.get("width"))+" "+str(item.get("height"))+" "+str(item.get("top").winfo_x())+" "+str(item.get("top").winfo_y())+"\n"
                    f.write(line)
                    item.get("image").save(path+"/"+str(i)+".png")
    def load_model(self,event):
        path = filedialog.askdirectory()
        with open(path+"/location.shot","r") as f:
            while True:
                line = f.readline()
                if not line:
                    break
                line = line.strip()
                info = line.split(" ")
                img = os.path.exists(path+"/"+info[0]+".png")
                if not img:
                    continue
                img = Image.open(path+"/"+info[0]+".png")
                self.cvs.append(self.image_show(img,self.path,self.root,self.control,width=int(info[1]),height=int(info[2]),winfox=int(info[3]),winfoy=int(info[4])))
                
                
    class image_show():
        def __init__(self,image,path,root,control,width=None,height=None,winfox=0,winfoy=0):
            self.image = image
            self.tempimg = image
            self.path=path+"/pictures/"
            self.control = control
            if(width==None or height==None):
                self.width,self.height = image.width,image.height
            else:
                self.width,self.height = width,height
                self.tempimg = self.tempimg.resize((self.width,self.height),Image.ANTIALIAS)
            self.top=tk.Toplevel(root)
            self.top.overrideredirect(True)
            self.x, self.y = winfox, winfoy
            self.img = ImageTk.PhotoImage(self.tempimg)
            self.canvas = tk.Canvas(self.top, width = self.width ,height = self.height,bd=0, bg = 'white')
            self.canvas.create_image(0,0,image = self.img,anchor="nw")
            self.canvas.pack()
            geo_str="+%s+%s" % (winfox, winfoy)
            self.top.geometry(geo_str)
            self.top.wm_attributes('-topmost',1)
            self.top.bind("<B1-Motion>",self.move)
            self.top.bind("<Button-1>",self.button_1)
            self.top.bind("<Double-Button-1>",self.change)
            
            self.top.bind("<"+self.control.getElementsByTagName("_1.5enlarge")[0].firstChild.data+">",self.mul1_5)
            self.top.bind("<"+self.control.getElementsByTagName("_0.5shrink")[0].firstChild.data+">",self.mul0_5)
            self.top.bind("<"+self.control.getElementsByTagName("flip_Updown")[0].firstChild.data+">",self.flip_ud)
            self.top.bind("<"+self.control.getElementsByTagName("flip_Leftright")[0].firstChild.data+">",self.flip_lr)
            self.top.bind("<"+self.control.getElementsByTagName("rotate_right90")[0].firstChild.data+">",self.rotate_right)
            self.top.bind("<"+self.control.getElementsByTagName("rotate_left90")[0].firstChild.data+">",self.rotate_left)
            
            self.top.bind("<"+self.control.getElementsByTagName("resetsingleshot")[0].firstChild.data+">",self.reset)
            self.top.bind("<"+self.control.getElementsByTagName("savescreenshot")[0].firstChild.data+">",self.save)
            self.top.bind("<"+self.control.getElementsByTagName("copyscreenshot")[0].firstChild.data+">",self.copy)
            self.top.bind("<MouseWheel>",self.zoom)
            self.top.bind("<"+self.control.getElementsByTagName("destorysingleshot")[0].firstChild.data+">",self.destroy)
        def button_1(self,event):
            self.x,self.y = event.x,event.y
        def move(self,event):
            new_x = (event.x-self.x)+self.top.winfo_x()
            new_y = (event.y-self.y)+self.top.winfo_y()
            geo_str="+%s+%s" % (new_x,new_y)
            self.top.geometry(geo_str)
        def destroy(self,event):
            self.image = None
            self.canvas.place_forget()
            self.top.destroy()
        def mul1_5(self,event):
            self.height=int(1.5*self.height)
            self.width=int(1.5*self.width)
            self.tempimg = self.tempimg.resize((self.width,self.height), Image.ANTIALIAS)
            self.img = ImageTk.PhotoImage(self.tempimg)
            self.canvas.destroy()
            self.canvas = tk.Canvas(self.top, height=self.height,width=self.width,bd=0, bg = 'white')
            self.canvas.create_image(0,0,image = self.img,anchor="nw")
            self.canvas.pack()
        def mul0_5(self,event):
            self.height=int(0.5*self.height)
            self.width=int(0.5*self.width)
            self.tempimg = self.tempimg.resize((self.width,self.height), Image.ANTIALIAS)
            self.img = ImageTk.PhotoImage(self.tempimg)
            self.canvas.destroy()
            self.canvas = tk.Canvas(self.top, height=self.height,width=self.width,bd=0, bg = 'white')
            self.canvas.create_image(0,0,image = self.img,anchor="nw")
            self.canvas.pack()
        def rotate_right(self,event):
            self.height,self.width=self.width,self.height
            self.tempimg = self.tempimg.transpose(Image.ROTATE_270)#顺时针旋转90
            self.img = ImageTk.PhotoImage(self.tempimg)
            self.canvas.destroy()
            self.canvas = tk.Canvas(self.top, height=self.height,width=self.width,bd=0, bg = 'white')
            self.canvas.create_image(0,0,image = self.img,anchor="nw")
            self.canvas.pack()
        def rotate_left(self,event):
            self.height,self.width=self.width,self.height
            self.tempimg = self.tempimg.transpose(Image.ROTATE_90)#逆时针旋转90
            self.img = ImageTk.PhotoImage(self.tempimg)
            self.canvas.destroy()
            self.canvas = tk.Canvas(self.top, height=self.height,width=self.width,bd=0, bg = 'white')
            self.canvas.create_image(0,0,image = self.img,anchor="nw")
            self.canvas.pack()
        def zoom(self,event):
            if(event.delta>0):
                self.width=int(1.1*self.width)
                self.height=int(1.1*self.height)
            else:
                self.width=int(0.9*self.width)
                self.height=int(0.9*self.height)
            self.tempimg = self.tempimg.resize((self.width,self.height),Image.ANTIALIAS)
            self.img = ImageTk.PhotoImage(self.tempimg)
            self.canvas.destroy()
            self.canvas = tk.Canvas(self.top, height=self.height,width=self.width,bd=0, bg = 'white')
            self.canvas.create_image(0,0,image = self.img,anchor="nw")
            self.canvas.pack()
        def flip_lr(self,event):
            self.tempimg = self.tempimg.transpose(Image.FLIP_LEFT_RIGHT)#左右镜像
            self.img = ImageTk.PhotoImage(self.tempimg)
            self.canvas.destroy()
            self.canvas = tk.Canvas(self.top, height=self.height,width=self.width,bd=0, bg = 'white')
            self.canvas.create_image(0,0,image = self.img,anchor="nw")
            self.canvas.pack()
        def flip_ud(self,event):
            self.tempimg = self.tempimg.transpose(Image.FLIP_TOP_BOTTOM)#垂直镜像
            self.img = ImageTk.PhotoImage(self.tempimg)
            self.canvas.destroy()
            self.canvas = tk.Canvas(self.top, height=self.height,width=self.width,bd=0, bg = 'white')
            self.canvas.create_image(0,0,image = self.img,anchor="nw")
            self.canvas.pack()
        def change(self,event):
            if(self.height>50 and self.width>50):
                self.tempimg = self.tempimg.resize((50,50),Image.ANTIALIAS)
                self.height = 50
                self.width = 50
                self.img = ImageTk.PhotoImage(self.tempimg)
                self.canvas.destroy()
                self.canvas = tk.Canvas(self.top, height=self.height,width=self.width,bd=0, bg = 'white')
                self.canvas.create_image(0,0,image = self.img,anchor="nw")
                self.canvas.pack()
            else:
                self.tempimg = self.image
                self.height = self.image.height
                self.width = self.image.width
                self.img = ImageTk.PhotoImage(self.tempimg)
                self.canvas.destroy()
                self.canvas = tk.Canvas(self.top, height=self.height,width=self.width,bd=0, bg = 'white')
                self.canvas.create_image(0,0,image = self.img,anchor="nw")
                self.canvas.pack()
        def reset(self,event):
            self.tempimg = self.image
            self.height = self.image.height
            self.width = self.image.width
            self.img = ImageTk.PhotoImage(self.tempimg)
            self.canvas.destroy()
            self.canvas = tk.Canvas(self.top, height=self.height,width=self.width,bd=0, bg = 'white')
            self.canvas.create_image(0,0,image = self.img,anchor="nw")
            self.canvas.pack()
        def copy(self,event):
            image = self.image
            output = BytesIO()
            image.save(output, 'BMP')
            data = output.getvalue()[14:]
            output.close()
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
            win32clipboard.CloseClipboard()
        def save(self,event):
            folder = os.path.exists(self.path)
            if not folder:
                os.makedirs(self.path)
            self.image.save(self.path+time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())+".png")
            
tools()