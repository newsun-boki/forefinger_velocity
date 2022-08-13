import json
import random
from paho.mqtt import client as mqtt_client
import time
import datetime
from math import ceil, floor
import matplotlib.pyplot as plt
import _thread

# 公共变量
broker = 'broker.emqx.io'
topic = "/python/mqtt/li"
port = 1883
client_id = f'python-mqtt-li-{random.randint(0, 100)}'

show_num = 100

mean_vs = []
pos_list = []
stime = []


"""mqtt subscribe topic"""
def str_microsecond_datetime2int_13timestamp(str_microsecond_datetime):
  """将字符串型【毫秒级】格式化时间 转为 【13位】整型时间戳"""
  datetime_obj = datetime.datetime.strptime(str_microsecond_datetime, "%Y/%m/%d-%H:%M:%S.%f")
  obj_stamp = int(time.mktime(datetime_obj.timetuple()) * 1000.0 + datetime_obj.microsecond / 1000.0) / 1000.0
  return obj_stamp


def int2datetime(int_float_timestamp):
  """
  有小数点：分离小数点，整数转为格式化时间，小数点直接跟在后面
  无小数点：从第10位进行分离，
  所以本函数只适用于时间戳整数位数大于9且小于11.
  """
  if '.' in str(int_float_timestamp):
      int_float = str(int_float_timestamp).split('.')
      date = time.localtime(int(int_float[0]))
      tempDate = time.strftime("%Y/%m/%d-%H:%M:%S", date)
      secondafter = '.' + str(int_float[1])
      return str(tempDate) + secondafter


def parse_mqttmsg(msg):
  """解析mqt头数据   MAC samplerate sampletime battery acc"""
  content = json.loads(msg.payload.decode())
  span = 1000 / content['samplerate'] * 10
  time_span = [ceil(span) / 10 / 1000, floor(span) / 10 / 1000]
  sampletime = content['sampletime']
  sampletime_int = str_microsecond_datetime2int_13timestamp(sampletime)
  acc = content['acc']
  mean_vs.append(acc)
  if len(mean_vs) > 100:
    del(mean_vs[0])
  pos = content['pos']


def connect_mqtt():
  def on_connect(client, userdata, flags, rc):
      if rc == 0:
          print("Connected to MQTT Broker!")
      else:
          print("Failed to connect, return code %d\n", rc)
          pass

  client = mqtt_client.Client(client_id)
  client.on_connect = on_connect
  client.connect(broker, port)
  return client


def subscribe(client: mqtt_client):
  def on_message(client, userdata, msg):
      # print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
      parse_mqttmsg(msg)

  client.subscribe(topic)
  client.on_message = on_message


def run():
  client = connect_mqtt()
  subscribe(client)
  client.loop_forever()


""" draw figures """
def draw_figure():
  plt.ion()  # 开启一个画图的窗口进入交互模式，用于实时更新数据
  plt.rcParams['figure.figsize'] = (10, 10)  # 图像显示大小
  plt.rcParams['font.sans-serif'] = ['SimHei']  # 防止中文标签乱码，还有通过导入字体文件的方法
  plt.rcParams['axes.unicode_minus'] = False
  plt.rcParams['lines.linewidth'] = 0.5  # 设置曲线线条宽度


  count = 0
  while True:
      plt.clf()  # 清除刷新前的图表，防止数据量过大消耗内存
      plt.suptitle("总标题", fontsize=30)  # 添加总标题，并设置文字大小
      plt.tight_layout()

      # 图表1
      agraphic = plt.subplot(2, 1, 1)
      agraphic.set_xlabel('x轴', fontsize=10)  # 添加轴标签
      agraphic.set_ylabel('y轴', fontsize=20)
      plt.plot(range(len(mean_vs)), mean_vs, 'g-')
  

      plt.pause(0.001)  # 设置暂停时间，太快图表无法正常显示


if __name__ == '__main__':
  # 多线程
  _thread.start_new_thread(run, ())
  draw_figure()