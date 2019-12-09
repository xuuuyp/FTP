import socket
import json  # json.dumps(some)打包   json.loads(some)解包
import tkinter
import tkinter.messagebox
from tkinter import filedialog
import time

IP = '127.0.0.1'
PORT = 50006
# 初始文件窗口
root1 = tkinter.Tk()
root1.title('Select initial address')
root1['width'] = 290
root1['height'] = 120

initial_address = tkinter.StringVar()
initial_address.set('/Users/xuuuyp/Desktop')

# 用户名标签
labelUser = tkinter.Label(root1, text='initial address')
labelUser.place(x=20, y=20, width=90, height=20)

entryUser = tkinter.Entry(root1, width=80, textvariable=initial_address)
entryUser.place(x=110, y=20, width=160, height=20)


# 登录按钮
def Enter(*args):
    global initial_address
    initial_address = entryUser.get()
    # 初始地址不能为空
    if not initial_address:
        tkinter.messagebox.showerror('Empty', message='Address Empty!')
    else:
        root1.destroy()       # 关闭窗口


root1.bind('<Return>', Enter)  # 回车绑定登录功能
but = tkinter.Button(root1, text='Enter', command=Enter)
but.place(x=100, y=70, width=70, height=30)
root1.mainloop()


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((IP, PORT))
s.send(initial_address.encode())  # 发送
# 创建图形界面
root = tkinter.Tk()
title = '≈百度网盘'
root.title(title)  # 窗口命名为用户名
root['height'] = 370
root['width'] = 300
root.resizable(0, 0)  # 限制窗口大小

list = ''  # 列表框
label = ''  # 显示路径的标签
upload = ''  # 上传按钮


def file_client():
    # 创建列表框
    list = tkinter.Listbox(root)
    list.place(x=0, y=30, width=300, height=280)

    # 将接收到的目录文件列表打印出来(dir), 显示在列表框中, 在pwd函数中调用
    def recv_list(enter):
        s.send(enter.encode())
        data = s.recv(4096)
        try:
            data = json.loads(data.decode())
            list.delete(0, tkinter.END)  # 清空列表框
            for i in range(len(data)):
                if '.' in data[i]:
                    list.insert(tkinter.END, ('' + data[i]))
                    list.itemconfig(tkinter.END, fg='blue')
        except:
            # 如果地址不存在
            print(data.decode())

    # 创建标签显示服务端工作目录
    def lab():
        global label
        try:
            label.destroy()
            label = tkinter.Label(root, text=initial_address)
            label.place(x=0, y=0, )
        except:
            label = tkinter.Label(root, text=initial_address)
            label.place(x=0, y=0, )
        recv_list('dir  ')

    # 刚连接上服务端时进行一次面板刷新
    lab()

    # 接收下载文件(get)
    def get(message):
        # print(message)
        name = message.split(' ')
        # print(name)
        name = name[1]  # 获取命令的第二个参数(文件名)
        # 选择对话框, 选择文件的保存路径
        fileName = tkinter.filedialog.asksaveasfilename(title='Save file to', initialfile=name)
        # 如果文件名非空才进行下载
        if fileName:
            s.send(message.encode())
            with open(fileName, 'wb') as f:
                while True:
                    data = s.recv(10240)
                    # print(data)
                    # if data == 'EOF'.encode():
                    #     tkinter.messagebox.showinfo(title='Message',
                    #                                 message='Download completed!')
                    #     break
                    time.sleep(2)

                    f.write(data)
                    tkinter.messagebox.showinfo(title='Message',
                                                message='Download completed!')
                    break

    # 创建用于绑定在列表框上的函数
    def run(*args):
        indexs = list.curselection()
        index = indexs[0]
        content = list.get(index)
        # 如果有一个 . 则为文件
        if '.' in content:
            content = 'get ' + content
            get(content)
            # cd('cd')
        # lab()  # 刷新显示页面

    # 在列表框上设置绑定事件
    list.bind('<ButtonRelease-1>', run)


# 关闭连接
def close_file():
    s.send('quit'.encode())
    print('exit file server')
    s.close()

file_client()
root.mainloop()
close_file()
