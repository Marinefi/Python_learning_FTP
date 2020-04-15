"""
ftp客户端
"""

from threading import Thread
from socket import *
import os
from time import sleep
import re

HOST = "127.0.0.1"
PORT = 8088
ADDR = (HOST, PORT)

Download_Fold = "/home/tarena/LJC/file_download/"


class FTPClient:
    def __init__(self, sockfp):
        self.sockfp = sockfp

    def do_list(self):
        self.sockfp.send(b"L ")  # 向服务器发送请求
        mes = self.sockfp.recv(1024).decode()  # 接受服务器发回的消息
        if mes == "YES":  # 接受到“YES”,
            data = self.sockfp.recv(1024)
            print(data.decode())
        else:
            print("文件列表获取失败\n原因：", mes)

    def do_download(self, file_name):
        message = "".join(["D ", file_name])
        self.sockfp.send(message.encode())  # 发送下载请求+文件名
        mes = self.sockfp.recv(1024).decode()
        if mes == "YES":  # 接受到“YES”,
            size = int(self.sockfp.recv(1024).decode())
            with open(Download_Fold + file_name, "wb") as f2:
                while size>1024:
                    data = self.sockfp.recv(1024)
                    f2.write(data)
                    size-=1024
                f2.write(self.sockfp.recv(size))
            print(self.sockfp.recv(128).decode())
        else:
            print("文件下载失败\n原因：", mes)

    def do_uploding(self, file_way):
        try:
            f2=open(file_way,"rb")
        except:
            print("文件不存在，无法上传")
            return
        file_name=file_way.split("/")[-1]
        message = "".join(["U ", file_name])
        self.sockfp.send(message.encode())  # 发送下载请求+文件名
        mes = self.sockfp.recv(1024).decode()
        if mes == "YES":  # 接受到“YES”,
            size = os.path.getsize(file_way)
            self.sockfp.send(b"%d" % size)
            sleep(0.1)
            data=f2.read(size)
            self.sockfp.send(data)
        mess=self.sockfp.recv(1024).decode()
        print(mess)

    def do_quit(self):
        print("正在与服务器断开连接")
        self.sockfp.send(b"Q ")
        self.sockfp.close()
        print("断开成功")



    def get_fold_info(self):
        file_list = os.listdir(Download_Fold)
        return "\n".join(file_list)


def main():
    sockfp = socket()
    sockfp.connect(ADDR)
    ftp = FTPClient(sockfp)

    while True:
        print("===================")
        print("1.获取文件列表------")
        print("2.下载文件----------")
        print("3.上传文件----------")
        print("4.退出-------------")

        try:
            cmd = input(">>")
        except:
            cmd="4"
        if cmd == "1":
            ftp.do_list()
        elif cmd == "2":
            file_name = input("输入需要下载的文件名")
            ftp.do_download(file_name)
        elif cmd == "3":
            file_way = input("输入需要上传的文件名(可使用路径)")
            ftp.do_uploding(file_way)
        elif not cmd or cmd =="4":
            ftp.do_quit()
            break

if __name__ == '__main__':
    main()
