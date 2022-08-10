from asyncio import Handle
from turtle import width
import cv2
import socket
from cvzone.HandTrackingModule import HandDetector
import time
import math
import threading
from matplotlib.pyplot import draw
import numpy as np

forefinger_pos_list = []
forefinger_v_list = np.array([0.0, 0.0, 0.0])
smooth_pos_list = []
mean_v_list = np.array([0.0, 0.0, 0.0])
last_point = np.array([0.0, 0.0, 0.0])
delta_time = 0
threadLock = threading.Lock()
#param
width,height = 1280,720
class Observer(threading.Thread):
    def __init__(self, threadID, name, delay):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.delay = delay
        self.points = []
        self.last_time = 0
        self.pred = 0
        self.main_point = np.array([0,0]);
    def calculatePoints(self):
        if(len(forefinger_pos_list) > 1):
            current_time = time.time_ns()
            delta_time = (current_time - self.last_time)/10e6;
            if(delta_time > 0):
                current_point = np.array(forefinger_pos_list[-1])
                current_mean = np.array(mean_v_list[-1])
                print(current_point)
                if(self.main_point[0] != current_point[0]):
                    self.main_point = current_point
                    self.pred = current_point + current_mean * delta_time
                    # print(self.pred)

                else:
                    self.pred = self.pred + current_mean * delta_time
                threadLock.acquire()
                # print(str(type(self.pred))," " , str(self.pred))
                if(abs(self.pred[0]) < 2e3):
                    # print(self.pred)
                    smooth_pos_list.append(self.pred)
                if(len(smooth_pos_list) > 300):
                    del(smooth_pos_list[0])
                threadLock.release()
                self.last_time = current_time
    def run(self):
        while True:
            # print ("开始线程：" + self.name)
            self.calculatePoints()
            

def velocityFilter(forefinger_pos, last_point, delta_time):
    forefinger_v_x = (forefinger_pos[0] - last_point[0]) / delta_time
    forefinger_v_y = (forefinger_pos[1] - last_point[1])/ delta_time
    forefinger_v_z = (forefinger_pos[2] - last_point[2])/ delta_time
    global forefinger_v_list
    forefinger_v_list = np.vstack([forefinger_v_list, np.array([forefinger_v_x,forefinger_v_y,forefinger_v_z])])
    if(forefinger_v_list.shape[0] > 4): # save 30 forefinger velocity
        forefinger_v_list = np.delete(forefinger_v_list, 0, axis=0)
    mean_v = np.mean(forefinger_v_list,axis=0)
    last_point[0] = forefinger_pos[0]
    last_point[1] = forefinger_pos[1]
    last_point[2] = forefinger_pos[2]
    return mean_v

def drawTrace(mean_v,img):
    img = cv2.circle(img,(forefinger_pos_list[-1][0],forefinger_pos_list[-1][1]),10,(255,0,0),-1) #draw current forefinger
    for p in smooth_pos_list:
        forefinger_v = mean_v
        # forefinger_v = 255 / (1 + math.exp(-forefinger_v))
        # img = cv2.line(img,(last_point[0],last_point[1]),(p[0],p[1]),(forefinger_v,forefinger_v,forefinger_v),2)
        img = cv2.circle(img,(int(p[0]),int(p[1])),4,(0,255,0),-1)
        # last_point = p
    for p in forefinger_pos_list:
    #     forefinger_v = mean_v
        # print(forefinger_v)
    #     # forefinger_v = 255 / (1 + math.exp(-forefinger_v))
    #     # img = cv2.line(img,(last_point[0],last_point[1]),(p[0],p[1]),(forefinger_v,forefinger_v,forefinger_v),2)
        img = cv2.circle(img,(p[0],p[1]),4,(255,0,0),-1)
    #     # last_point = p
    
    
    

def Main():
    #video setting
    cap = cv2.VideoCapture(1)
    cap.set(3,width)
    cap.set(4,height)
    #detector setting
    detector = HandDetector(maxHands=1,detectionCon=0.8)
    last_time = 0
    global delta_time
    current_time = 0
    observer = Observer(1,"Observer",1)
    observer.setDaemon(True)
    observer.start()
    while True:
        success,img = cap.read()
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

            #get timestamp 
            current_time = time.time_ns() 
            delta_time = (current_time - last_time)/10e6

            #compute velocity
            mean_v = velocityFilter(forefinger_pos, last_point, delta_time)
            global mean_v_list
            mean_v_list = np.vstack([mean_v_list,mean_v])
            if(len(mean_v_list) > 30): # save 30 mean_v
                mean_v_list = np.delete(mean_v_list,0,axis=0)
            drawTrace(mean_v,img)
        img=cv2.resize(img,(0,0),None,0.5,0.5)
        last_time = current_time
        cv2.imshow("image",img)
        cv2.waitKey(1)

if __name__ == "__main__":
    Main()