"""
服务器端（多进程）
"""

from threading import Thread
from socket import *
import sys, os
from time import sleep

HOST = "127.0.0.1"
PORT = 8088
ADDR = (HOST, PORT)
Fold = "/home/tarena/FTP_file/"


class MyFtpThread(Thread):

    def __init__(self, connect_socket=None):
        super().__init__()
        self.connect_socket = connect_socket

    def do_list(self):
        file_mes = self.get_fold_info()
        if file_mes:  # 文件列表不为空
            self.connect_socket.send(b"YES")
            sleep(0.1)
            self.connect_socket.send(file_mes.encode())
        else:
            self.connect_socket.send("文件列表为空".encode())

    def do_download(self, file_name):
        file_mes = self.get_fold_info()
        if file_name in file_mes:  # 文件列表中包含改文件
            #print("文件存在")
            self.connect_socket.send(b"YES")
            sleep(0.1)
            size = os.path.getsize(Fold + file_name)
            self.connect_socket.send(b"%d" % size)
            sleep(0.1)
            with open(Fold + file_name, "rb") as f1:
                while True:
                    data = f1.read(1024)
                    if not data:
                        break
                    self.connect_socket.send(data)
            sleep(0.1)
            self.connect_socket.send("下载成功".encode())
        else:
            self.connect_socket.send("文件不存在".encode())

    def do_uploading(self, file_name):
        self.connect_socket.send(b"YES")
        size = int(self.connect_socket.recv(1024).decode())
        with open(Fold + file_name, "wb") as f1:
            data = self.connect_socket.recv(size)
            f1.write(data)
        self.connect_socket.send("上传成功")



    def get_fold_info(self):
        file_list = os.listdir(Fold)
        return "\n".join(file_list)

    # 文件列表获取失败
    # 原因： YES

    def run(self):
        print("a client is connected...")
        while True:
            data = self.connect_socket.recv(1024)
            mes = data.decode().split(" ", 2)
            if not mes and mes[0]=="Q":#退出请求
                return#退出run函数,相当于退出线程
            elif mes[0] == "L":
                self.do_list()
            elif mes[0] == "D":
                self.do_download(mes[1])  # 将文件名传递过去
            elif mes[0] == "U":  # 上传文件请求
                self.do_uploading(mes[1])



def main():
    sock = socket()
    sock.bind(ADDR)
    sock.listen(10)
    print("server is running...")
    while True:
        try:
            connect_socket, addr = sock.accept()
        except:
            sys.exit("服务器退出")  # 主进程退出
        t = MyFtpThread(connect_socket)
        t.setDaemon(True)  # 主服务退出,子进程也退出
        t.start()


if __name__ == '__main__':
    main()
