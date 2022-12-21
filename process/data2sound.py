'''
播放特定頻率
'''
import numpy as np
import pyaudio
import socket
import _thread
volume = 0
def sine(frequency, t, sampleRate):
    '''
    產生 sin wave
 
    :Args:
     - frequency: 欲產生的頻率 Hz
     - t: 播放時間長度 seconds
     - sampleRate: 取樣頻率 1/s
    '''
    # 播放數量
    n = int(t * sampleRate)
    # 每秒轉動的角度再細分為取樣間隔
    interval = 2 * np.pi * frequency / sampleRate
    return np.sin(np.arange(n) * interval)
 
 
def play_tone(stream, volume,frequency=440, t=1, sampleRate=44100):
    '''
    播放特定頻率
 
    :Args:
     - stream: 
     - frequency: 欲產生的頻率 Hz
     - t: 播放時間長度 seconds
     - sampleRate: 取樣頻率 1/s
    '''
    data = sine(frequency, t, sampleRate)
    
    # 因 format 為  pyaudio.paFloat32，故轉換為 np.float32 並轉換為 bytearray
    stream.write(volume* data.astype(np.float32).tostring())
    print("volume")
    print(volume)
 
def get_v(v,stream,volume):
    # print(v*1000)
    play_tone(stream,volume,frequency= v* 1000,t = 0.001)

def getVolume( threadName):
    ip_port = ('127.0.0.1', 9999)
    sk = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
    sk.bind(ip_port)
    global volume
    while True:
        volume = int(sk.recv(1024).strip().decode())

def playaudio(qv):
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paFloat32,
                    channels=1, rate=44100, output=True)
    
    try:
        _thread.start_new_thread( getVolume, ("Thread-1", ) )
    except:
        print ("Error: 无法启动线程")
    global volume
    while True:
        if qv.empty() == False:
            v = qv.get()
            get_v(v,stream,volume)
if __name__ == '__main__':
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paFloat32,
                    channels=1, rate=44100, output=True)
    for i in range(1000):
        play_tone(stream, 
        frequency=i, #Hz
        t=0.1) #seconds
 
    stream.close()
    p.terminate()