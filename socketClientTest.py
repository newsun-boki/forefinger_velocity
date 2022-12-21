# 客户端
import socket
ip_port = ('127.0.0.1', 9999)

sk = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
while True:
    inp = input('发送的消息：').strip()
    sk.sendto(inp.encode(), ip_port)
    if inp == 'exit':
        break

sk.close()