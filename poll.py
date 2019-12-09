import select
import f

addr = ''
initial_address = ''


def all_events_forver(poll_object):
    while True:
        for fd, event in poll_object.poll():
            yield fd, event


def server(listener):
    global addr, initial_address
    s = {listener.fileno(): listener}
    addresses = {}
    bytes_received = {}
    to_send = {}

    poll_object = select.poll()
    poll_object.register(listener, select.POLLIN)

    for fd, event in all_events_forver(poll_object):
        sock = s[fd]

        if event & (select.POLLHUP | select.POLLERR | select.POLLNVAL):
            address = addresses.pop(sock)
            rb = bytes_received.pop(sock, b'')
            sb = to_send.pop(sock, b'')
            if rb:
                print('client {} send {} but then closed'.format(address, rb))
            elif sb:
                print('client {} closed before we sent'.format(address))
            else:
                print('client {} closed socket normally'.format(address))
            poll_object.unregister(fd)
            del s[fd]

        elif sock is listener:
            sock, addr = sock.accept()
            print('new connection {}'.format(addr))
            sock.setblocking(False)
            s[sock.fileno()] = sock
            addresses[sock] = addr
            poll_object.register(sock, select.POLLIN)

        elif event & select.POLLIN:
            more_data = sock.recv(4096)
            if more_data.decode() == 'quit':
                # print('Disconnected from {0}'.format(addr))
                sock.close()
                continue
            else:
                data = bytes_received.pop(sock, b'') + more_data
                order = data.split(b' ')[0]  # 获取动作
                if order == b'get':
                    to_send[sock] = f.send_file(data.decode(), initial_address)
                    # to_send[sock] = b'EOF'
                    # 此处也为bug，不能一次添加两个to_send只会发送最后添加的
                    # sock.send(function.send_file(data.decode(), initial_address))
                    # print(zen.send_file(data.decode(), initial_address))
                    # time.sleep(0.1)  # 延时确保文件发送完整
                    # to_send[sock] = function.finish_file()
                    poll_object.modify(sock, select.POLLOUT)
                elif order == b'dir':
                    to_send[sock] = f.send_list(initial_address)
                    poll_object.modify(sock, select.POLLOUT)
                else:
                    initial_address = more_data.decode()
                    # 此处为bug，写入报告
                    # to_send[sock] = zen.send_list(initial_address)
                    # poll_object.modify(sock, select.POLLOUT)

        elif event & select.POLLOUT:
            data = to_send.pop(sock)
            print(data)
            n = sock.send(data)
            if n < len(data):
                to_send[sock] = data[n:]
            else:
                poll_object.modify(sock, select.POLLIN)


if __name__ == "__main__":
    IP = '127.0.0.1'
    PORT = 50006
    ADDR = (IP, PORT)
    listener = f.create_socket(ADDR)
    server(listener)
