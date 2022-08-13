import random
import time
from paho.mqtt import client as mqtt_client
import json
from datetime import datetime

broker = 'broker.emqx.io'
port = 1883
topic = "/python/mqtt/li"
client_id = f'python-mqtt-{random.randint(0, 1000)}'  # 随机生成客户端id


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
  while True:
      time.sleep(0.01)
      msg = json.dumps({"MAC": "0123456789",
                        "samplerate": 12,
                        "sampletime": str(datetime.utcnow().strftime('%Y/%m/%d-%H:%M:%S.%f')[:-3]),
                        "battery": 0.5,
                        "acc": [
                            [random.randint(200, 350), -random.randint(200, 350), -random.randint(200, 350), random.randint(200, 350), random.randint(200, 350), random.randint(200, 350)],
                            [random.randint(200, 350), -random.randint(200, 350), -random.randint(200, 350), random.randint(200, 350), random.randint(200, 350), random.randint(200, 350)],
                            [random.randint(200, 350), -random.randint(200, 350), -random.randint(200, 350), random.randint(200, 350), random.randint(200, 350), random.randint(200, 350)],
                            [random.randint(200, 350), -random.randint(200, 350), -random.randint(200, 350), random.randint(200, 350), random.randint(200, 350), random.randint(200, 350)],
                            [random.randint(200, 350), -random.randint(200, 350), -random.randint(200, 350), random.randint(200, 350), random.randint(200, 350), random.randint(200, 350)],
                            [random.randint(200, 350), -random.randint(200, 350), -random.randint(200, 350), random.randint(200, 350), random.randint(200, 350), random.randint(200, 350)],
                            [random.randint(200, 350), -random.randint(200, 350), -random.randint(200, 350), random.randint(200, 350), random.randint(200, 350), random.randint(200, 350)],
                            [random.randint(200, 350), -random.randint(200, 350), -random.randint(200, 350), random.randint(200, 350), random.randint(200, 350), random.randint(200, 350)],
                            [random.randint(200, 350), -random.randint(200, 350), -random.randint(200, 350), random.randint(200, 350), random.randint(200, 350), random.randint(200, 350)],
                            [random.randint(200, 350), -random.randint(200, 350), -random.randint(200, 350), random.randint(200, 350), random.randint(200, 350), random.randint(200, 350)],
                            [random.randint(200, 350), -random.randint(200, 350), -random.randint(200, 350), random.randint(200, 350), random.randint(200, 350), random.randint(200, 350)],
                            [random.randint(200, 350), -random.randint(200, 350), -random.randint(200, 350), random.randint(200, 350), random.randint(200, 350), random.randint(200, 350)],
                        ]})
      result = client.publish(topic, msg)
      status = result[0]
      if status == 0:
          print(f"Send  to topic `{topic}`")
      else:
          print(f"Failed to send message to topic {topic}")


def run():
  client = connect_mqtt()
  client.loop_start()
  publish(client)


if __name__ == '__main__':
  run()