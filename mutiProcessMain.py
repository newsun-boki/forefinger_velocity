from asyncio import Handle
from re import X
from turtle import width
import cv2
import socket
from cvzone.HandTrackingModule import HandDetector
import time
import math
import threading
# from matplotlib.pyplot import draw
import numpy as np
import matplotlib.pyplot as plt
from multiprocessing import Process,Queue

import pyqt5graph
from PyQt5.Qt import *
from pyqtgraph import PlotWidget
from PyQt5 import QtCore

forefinger_campos_list = []
forefinger_pos_list = []
forefinger_v_list = np.array([0.0, 0.0, 0.0])
forefinger_a_list = np.array([0.0, 0.0, 0.0])
smooth_pos_list = []
smooth_v_list = []
mean_a = 0
mean_v_list = np.array([0.0, 0.0, 0.0])
last_point = np.array([0.0, 0.0, 0.0])
last_v = np.array([0.0, 0.0, 0.0])
delta_time = 0
threadLock = threading.Lock()
#param
width,height = 640,480

def observeVelocityFilter(campos, last_campos, delta_time,last_camv):
    if delta_time != 0.0:
        cam_vx = (campos[0] - last_campos[0]) / delta_time
        cam_vy = (campos[1] - last_campos[1])/ delta_time
        cam_vz = (campos[2] - last_campos[2])/ delta_time
        cam_v =  np.array([cam_vx,cam_vy, cam_vz])
        cam_v = (0.2* cam_v + last_camv * 0.8).copy()
        last_camv = cam_v.copy() 
    else:
        cam_v = last_camv.copy() 
    return cam_v

def observeAcceleratorFilter(cam_v,last_camv,delta_time,last_cama):
    if delta_time != 0.0:
        cam_ax = (cam_v[0] - last_camv[0]) / delta_time
        cam_ay = (cam_v[1] - last_camv[1])/ delta_time
        cam_az = (cam_v[2] - last_camv[2])/ delta_time
        cam_a = (0.2 * np.array([cam_ax,cam_ay, cam_az]) + 0.8 * last_cama).copy()
        last_cama = cam_a.copy()
    else:
        cam_a = last_cama.copy() 
    return cam_a

def calculate(campos,delta_time,last_campos,last_camv, last_cama):
    # print(campos,delta_time,last_campos,last_camv)
    cam_v = observeVelocityFilter(campos, last_campos, delta_time,last_camv)
    cam_a = observeAcceleratorFilter(cam_v,last_camv,delta_time,last_cama)
    return cam_v,cam_a

#多进程
def observe(q,qv):

    last_time_slow = time.time_ns()
    last_time_fast = time.time_ns()
    campos = np.array([0.0, 0.0, 0.0])
    last_campos = np.array([0.0, 0.0, 0.0])
    last_camv = np.array([0.0, 0.0, 0.0])
    campos_list = []
    camv_list = []
    last_cama = np.array([0.0, 0.0, 0.0])
    cam_v = 0
    cam_a = 0
    campos_pred = np.array([0.0, 0.0, 0.0])
    camv_pred = np.array([0.0, 0.0, 0.0])
    data=open("data.txt",'w+') 
    while True: 
        current_time = time.time_ns()
        if q.empty() == False :
            delta_time = (current_time - last_time_slow)/10e5 # ms
            campos = q.get()
            campos_list.append(campos)
            cam_v,cam_a = calculate(campos,delta_time,last_campos,last_camv, last_cama)
            last_time_slow = current_time
            last_campos = campos.copy()
            campos_pred = campos
            camv_pred = cam_v
        else:
            delta_time = (current_time - last_time_fast)/10e5 # ms
            campos_pred = campos_pred + cam_v * delta_time
            camv_pred = camv_pred + camv_pred * cam_a
            
            last_time_fast = current_time
        v = np.sqrt((camv_pred*camv_pred).sum())
        camv_list.append(v)
        qv.put(v)
        if(qv.qsize() > 10):
            qv.get()
        if len(camv_list) > 100:
            del(camv_list[0])

def qtplot(qv:Queue):
    import sys
    # PyQt5 程序固定写法
    app = QApplication(sys.argv)

    # 将绑定了绘图控件的窗口实例化并展示
    window = pyqt5graph.Window(qv)
    window.show()

    # PyQt5 程序固定写法
    sys.exit(app.exec())

def velocityFilter(forefinger_pos, last_point, delta_time):
    forefinger_v_x = (forefinger_pos[0] - last_point[0]) / delta_time
    forefinger_v_y = (forefinger_pos[1] - last_point[1])/ delta_time
    forefinger_v_z = (forefinger_pos[2] - last_point[2])/ delta_time
    global forefinger_v_list
    forefinger_v_list = np.vstack([forefinger_v_list, np.array([forefinger_v_x,forefinger_v_y,forefinger_v_z])])
    if(forefinger_v_list.shape[0] > 3): # save 30 forefinger velocity
        forefinger_v_list = np.delete(forefinger_v_list, 0, axis=0)
    mean_v = np.mean(forefinger_v_list,axis=0)
    last_point[0] = forefinger_pos[0]
    last_point[1] = forefinger_pos[1]
    last_point[2] = forefinger_pos[2]
    return mean_v
    # accelerator 
def acceleratorFilter(mean_v, last_v, delta_time):
    forefinger_a_x = (mean_v[0] - last_v[0]) / delta_time
    forefinger_a_y = (mean_v[1] - last_v[1])/ delta_time
    forefinger_a_z = (mean_v[2] - last_v[2])/ delta_time
    global forefinger_a_list
    forefinger_a_list = np.vstack([forefinger_a_list, np.array([forefinger_a_x,forefinger_a_y,forefinger_a_z])])
    if(forefinger_a_list.shape[0] > 5): # save 30 forefinger velocity
        forefinger_a_list = np.delete(forefinger_a_list, 0, axis=0)
    mean_a = np.mean(forefinger_a_list,axis=0)
    last_v[0] = mean_v[0]
    last_v[1] = mean_v[1]
    last_v[2] = mean_v[2]
    return mean_a

def drawTrace(mean_v_list,img):
    img = cv2.circle(img,(forefinger_pos_list[-1][0],forefinger_pos_list[-1][1]),10,(0,255,0),-1) #draw current forefinger
    for p in smooth_pos_list:
        # forefinger_v = mean_v
        # forefinger_v = 255 / (1 + math.exp(-forefinger_v))
        # img = cv2.line(img,(last_point[0],last_point[1]),(p[0],p[1]),(forefinger_v,forefinger_v,forefinger_v),2)
        img = cv2.circle(img,(int(p[0]),int(p[1])),4,(0,255,0),-1)
        # last_point = p
    for i in range(len(forefinger_pos_list)):
        p = forefinger_pos_list[i]
        v = mean_v_list[i]
        v = np.sqrt((v*v).sum())  * 35
        img = cv2.circle(img,(int(p[0]),int(p[1])),4,(255 - int(v),0,int(v)),-1)

def pixel2cam(forefinger_pos, z_cam, camera_matrix):
    x_cam =z_cam / camera_matrix[0,0] * (forefinger_pos[0] - camera_matrix[0,2])
    y_cam = z_cam / camera_matrix[1,1] * (forefinger_pos[1] - camera_matrix[1,2])
    return x_cam, y_cam
    
def plotdata():
    if(len(forefinger_pos_list) > 28):
        plt.clf()
        plt.xlim((0, 480))
        plt.ylim((0, 640))
        # plt.plot(np.arange(len(forefinger_pos_list)), np.array(forefinger_pos_list)[:,0])
        v = mean_v_list[-1]
        v = np.sqrt((v*v).sum())
        if v > 5 : 
            v = 1
        else: 
            v = v / 5
        plt.plot(np.array(forefinger_pos_list)[:,0],640 - np.array(forefinger_pos_list)[:,1], color = (v,0,1 - v))
        plt.draw()
        plt.pause(0.01)

def Main():
    # plt.ion()
    # plt.figure(1)
    q = Queue()
    qv = Queue()
    z_cam = 470
    camera_matrix = np.zeros((3, 3))
    camera_matrix[0, 0] = 609.592345495693
    camera_matrix[1, 1] = 608.224584386026
    camera_matrix[0, 2] = 319.829953439972
    camera_matrix[1, 2] = 236.764106807809
    camera_matrix[2, 2] = 1
    distCoeffs = np.float32([-0.455846898828797,0.263364196795679,0, 0])
    
    #video setting
    cap = cv2.VideoCapture(1)
    cap.set(3,width)
    cap.set(4,height)
    #detector setting
    detector = HandDetector(maxHands=1,detectionCon=0.8)
    last_time = 0
    global delta_time
    global mean_a
    current_time = 0
    p = Process(target=observe,args=(q,qv))
    plot = Process(target=qtplot,args=(qv,))
    p.start()
    plot.start()
    while True:
        success,img = cap.read()
        img = cv2.undistort(img,camera_matrix,distCoeffs)
        hands,img = detector.findHands(img)
    # landmark values - (x,y,z)*21
        if hands: 
            #Get first hand 
            hand = hands[0]
            lmList = hand['lmList']

            #get forefinger_pos
            forefinger_pos = lmList[8] #x,y,z
            forefinger_pos_list.append(forefinger_pos)
            if(len(forefinger_pos_list) > 30): # save 30 forefinger pos
                del(forefinger_pos_list[0])
            x_cam, y_cam = pixel2cam(forefinger_pos,z_cam,camera_matrix)
            forefinger_campos = [x_cam,y_cam,z_cam]
            q.put(np.array(forefinger_campos))
            forefinger_campos_list.append(forefinger_campos)
            #get timestamp 
            current_time = time.time_ns() 
            delta_time = (current_time - last_time)/10e6

            #compute velocity
            mean_v = velocityFilter(forefinger_campos, last_point, delta_time)
            mean_a = acceleratorFilter(mean_v, last_v, delta_time)
            global mean_v_list
            mean_v_list = np.vstack([mean_v_list,mean_v])
            if(len(mean_v_list) > 30): # save 30 mean_v
                mean_v_list = np.delete(mean_v_list,0,axis=0)
            drawTrace(mean_v_list,img)
            # plotdata()

        # img=cv2.resize(img,(0,0),None,0.5,0.5)
        last_time = current_time
        cv2.imshow("image",img)
        cv2.waitKey(1)

if __name__ == "__main__":
    Main()