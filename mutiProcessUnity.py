

# from matplotlib.pyplot import draw
from turtle import pos
import numpy as np
from multiprocessing import Process,Queue

from PyQt5.Qt import *
import socket

from process.observer import observe
from process.pyqt5graph import qtplot
from process.data2sound import playaudio


def Main():

    client = socket.socket(type=socket.SOCK_DGRAM)
    client.bind(('127.0.0.1',5052))

    q = Queue()
    qv = Queue()
    p = Process(target=observe,args=(q,qv))
    plot = Process(target=qtplot,args=(qv,))
    audio = Process(target=playaudio,args=(qv,))
    p.start()
    plot.start()
    # audio.start()
    while True:
        
        re_Data,address = client.recvfrom(1024)
        # print('server>>',re_Data.decode('utf-8'))
        pos_str = re_Data.decode('utf-8')
        pos_str = pos_str.split(",")
        x = float(pos_str[0])
        y = float(pos_str[1])
        z = float(pos_str[1])
        forefinger_pos = np.array([x,y,z]) * 1000
        print(forefinger_pos)
        q.put(np.array(forefinger_pos))
       
    client.close()

if __name__ == "__main__":
    Main()