import socket
import threading
import json  # json.dumps(some)打包   json.loads(some)解包
import time
import os
import os.path
import sys
import argparse
import poll
import f

IP = '127.0.0.1'
PORT = 50006
initial_address = ''


# 传输当前目录列表
def send_list(conn):
    global initial_address
    try:
        # print(initial_address)
        listdir = os.listdir(initial_address)
        listdir = json.dumps(listdir)
        conn.sendall(listdir.encode())
    except:
        msg = 'address not exist, please try again'
        conn.sendall(msg.encode())


# 发送文件函数
def send_file(message, conn):
    global initial_address
    name = message.split()[1]  # 获取第二个参数(文件名)
    fileName = initial_address + '/' + name
    # fileName = r'./' + name
    with open(fileName, 'rb') as f:
        while True:
            a = f.read(1024)
            if not a:
                break
            conn.send(a)
    time.sleep(0.1)  # 延时确保文件发送完整
    conn.send('EOF'.encode())


# 判断输入的命令并执行对应的函数
def recv_func(order, message, conn):
    if order == 'get':
        return send_file(message, conn)
    elif order == 'dir':
        return send_list(conn)
    # elif order == 'cd':
    #     return cd(conn)


def connect(conn, addr):
    global initial_address
    print('Connected by: ', addr)
    initial_address = conn.recv(1024)  # 接收用户名
    initial_address = initial_address.decode()

    while True:
        data = conn.recv(1024)
        data = data.decode()
        if data == 'quit':
            print('Disconnected from {0}'.format(addr))
            break
        order = data.split(' ')[0]  # 获取动作
        recv_func(order, data, conn)
    conn.close()


def file_0(PORT):
    ADDR = (IP, PORT)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # 地址复用
    s.bind(ADDR)  # 绑定地址（端口号）
    s.listen(1000)  # 设置监听（最大连接数）
    print('File server starts running at:{}'.format(ADDR))
    while True:
        conn, addr = s.accept()
        connect(conn, addr)


class FileServer1(threading.Thread):
    def __init__(self, port):
        threading.Thread.__init__(self)
        self.ADDR = (IP, port)
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # 地址复用

    def tcp_connect(self, conn, addr):
        global initial_address
        print('Connected by: ', addr)
        initial_address = conn.recv(1024)  # 接收用户名
        initial_address = initial_address.decode()

        while True:
            data = conn.recv(1024)
            data = data.decode()
            if data == 'quit':
                print('Disconnected from {0}'.format(addr))
                break
            order = data.split(' ')[0]  # 获取动作
            recv_func(order, data, conn)

        conn.close()

    def run(self):
        self.s.bind(self.ADDR)
        self.s.listen(3)
        print('File server starts running at:{}'.format(self.ADDR))
        while True:
            conn, addr = self.s.accept()
            t = threading.Thread(target=self.tcp_connect, args=(conn, addr))
            t.start()
        self.s.close()


def file_1(PORT):
    f_server = FileServer1(PORT)
    f_server.start()
    while True:
        time.sleep(1)
        if not f_server.isAlive():
            print("File connection lost...")
            sys.exit(0)


def file_2(PORT):
    ADDR = (IP, PORT)
    listener = f.create_socket(ADDR)
    poll.server(listener)


if __name__ == '__main__':
    choices = {'0': file_0, '1': file_1, '2': file_2}
    parser = argparse.ArgumentParser(
        description='(1) Single-threaded'
                    '(2) Multi-threaded'
                    '(3) poll')
    parser.add_argument('way', choices=choices, help='Which way to choose')
    args = parser.parse_args()
    function = choices[args.way]
    function(PORT)

