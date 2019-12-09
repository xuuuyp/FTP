import socket
import json  # json.dumps(some)打包   json.loads(some)解包
import os
import os.path


def create_socket(ADDR):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # 地址复用
    s.bind(ADDR)    # 绑定地址（端口号）   
    s.listen(1000)    # 设置监听（最大连接数）
    print('File server starts running at:{}'.format(ADDR))
    return s


def accept_connection(s):
    while True:
        conn, addr = s.accept()
        print('client {} has connected'.format(addr))
        connect(conn, addr)


# 传输当前目录列表
def send_list(initial_address):
    try:
        listdir = os.listdir(initial_address)
        listdir = json.dumps(listdir)
        # conn.sendall(listdir.encode())
        return listdir.encode()
    except:
        msg = 'address not exist, please try again'
        return msg.encode()
        # conn.sendall(msg.encode())


# 发送文件函数
def send_file(message, initial_address):
    name = message.split()[1]  # 获取第二个参数(文件名)
    fileName = initial_address + '/' + name
    # fileName = r'./' + name
    with open(fileName, 'rb') as f:
        while True:
            # 这里有问题，不能再加个0了
            a = f.read(10240)
            if not a:
                break
            return a
    #         conn.send(a)
    # time.sleep(0.1)  # 延时确保文件发送完整
    # conn.send('EOF'.encode())


def finish_file():
    return 'EOF'.encode()


# 判断输入的命令并执行对应的函数
def recv_func(order, message, conn):
    if order == 'get':
        send_file(message, conn)
    elif order == 'dir':
        send_list(conn)


def connect(conn, addr):
    try:
        while True:
            request(conn,addr)
    # except EOFError:
    #     print('clinet {} has closed'.format(addr))
    # except Exception as e:
    #     print('client {} error:{}'.format(addr, e))
    finally:
        conn.close
        

def request(conn,addr):
    global initial_address
    initial_address = conn.recv(1024)  # 接收初始地址
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
    

