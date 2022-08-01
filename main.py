from asyncio import Handle
from turtle import width
import cv2
import socket
from cvzone.HandTrackingModule import HandDetector
import time
import math

#param
width,height = 1280,720


cap = cv2.VideoCapture(1)
cap.set(3,width)
cap.set(4,height)

detector = HandDetector(maxHands=1,detectionCon=0.8)

sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
serverAddressPort = ("127.0.0.1",5052)
print("1")
cnt = 0
forefinger_pos_list = []
# start =time.time()
while True:
    success,img = cap.read()
    
    hands,img = detector.findHands(img)
    # end = time.time()
    cnt = cnt + 1
    # print('Running time: %s Seconds'%((end-start)/cnt))
    data = []
    forefinger_v = 0
# landmark values - (x,y,z)*21
    if hands: 
        #Get first hand 
        hand = hands[0]
        lmList = hand['lmList']
        forefinger_pos = lmList[8] #x,y,z
        forefinger_pos_list.append(forefinger_pos)
        if(len(forefinger_pos_list) > 30):
            del(forefinger_pos_list[0])
        img = cv2.circle(img,(forefinger_pos[0],forefinger_pos[1]),10,(255,0,0),-1)
        last_point = [0,0]
        
        for p in forefinger_pos_list:
            if(last_point[0] != 0):
                forefinger_v = math.sqrt(math.pow(p[0] - last_point[0],2) + math.pow(p[1] - last_point[1],2)) * 3
                print(forefinger_v)
                # forefinger_v = 255 / (1 + math.exp(-forefinger_v))
                
                img = cv2.line(img,(last_point[0],last_point[1]),(p[0],p[1]),(forefinger_v,forefinger_v,forefinger_v),2)
                img = cv2.circle(img,(p[0],p[1]),2,(forefinger_v,forefinger_v,forefinger_v),-1)
            last_point = p
            
        # for lm in lmList:
        #     data.extend([lm[0],height - lm[1],lm[2]])
        # sock.sendto(str.encode(str(data)),serverAddressPort)
    # img=cv2.resize(img,(0,0),None,0.5,0.5)

    cv2.imshow("image",img)
    cv2.waitKey(1)