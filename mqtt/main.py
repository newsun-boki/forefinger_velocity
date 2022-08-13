import cv2
from cvzone.HandTrackingModule import HandDetector
import time
import math
import threading
# from matplotlib.pyplot import draw
import numpy as np
import matplotlib.pyplot as plt
import random
import time
from paho.mqtt import client as mqtt_client
import json
from datetime import datetime

broker = 'broker.emqx.io'
port = 1883
topic = "/python/mqtt/li"
client_id = f'python-mqtt-{random.randint(0, 1000)}'  # 随机生成客户端id

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


def connect_mqtt():
  def on_connect(client, userdata, flags, rc):
      if rc == 0:
          print("Connected to MQTT Broker!")
      else:
          print("Failed to connect, return code %d\n", rc)

  client = mqtt_client.Client(client_id)
  client.on_connect = on_connect
  client.connect(broker, port)
  return client


def publish(client):
    v = mean_v_list[-1]
    v = float(np.sqrt((v*v).sum()))
    msg = json.dumps({"MAC": "0123456789",
                        "samplerate": 12,
                        "sampletime": str(datetime.utcnow().strftime('%Y/%m/%d-%H:%M:%S.%f')[:-3]),
                        "battery": 0.5,
                        "acc": v,
                        "pos": [int(forefinger_pos_list[-1][0]), int(forefinger_pos_list[-1][1]),int(forefinger_pos_list[-1][2])]   
                        })
    result = client.publish(topic, msg)
    status = result[0]
    if status == 0:
        print(f"Send `{msg}` to topic `{topic}`")
    else:
        print(f"Failed to send message to topic {topic}")




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

    # accelerator
    return mean_v
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
    plt.ion()
    plt.figure(1)
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
    # observer = Observer(1,"Observer",1)
    # observer.setDaemon(True)
    # observer.start()
    client = connect_mqtt()

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
            publish(client)


        # img=cv2.resize(img,(0,0),None,0.5,0.5)
        last_time = current_time
        cv2.imshow("image",img)
        cv2.waitKey(1)

if __name__ == "__main__":
    Main()