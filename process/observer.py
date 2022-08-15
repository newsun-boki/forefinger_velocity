import numpy as np
import time
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
    cnt = 0
    start_time = time.time_ns()
    while True: 
        cnt = cnt + 1
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
        if v < 0.01:
            v = 0.0
        if v < 1:
            camv_list.append(v)
            print(v)
            qv.put(v)
            if(qv.qsize() > 10):
                qv.get()
            if len(camv_list) > 100:
                del(camv_list[0])