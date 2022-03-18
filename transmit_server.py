# MQTTLens

import paho.mqtt.client as mqtt
import datetime

# data = [{'id': f'{cctv_name}_{num + 1}', 'top': y, 'left': x,'update': str(datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S'))}]
def put(data):
    try:
        topic='data'
        clientId="tester1"
        mqttHost="13.125.166.98"
        mqttPort=1883

        pubClt=mqtt.Client(clientId)
        pubClt.connect(mqttHost,mqttPort)

        pubClt.loop_start()
        pubClt.publish(topic,data,1)
        pubClt.loop_stop()
        print(f'Success publishing data')
    except Exception as e:
        print(f'failed publishing data: {e}')


if __name__ == '__main__':
    while True:
        put("[{'id': 'CCTV20_1', 'top': 1805, 'left': 2438, 'update': '2022-03-18-16-40-05'}, {'id': 'CCTV21_1', 'top': 2305, 'left': 1221, 'update': '2022-03-18-16-40-05'}, {'id': 'CCTV22_1', 'top': 1390, 'left': 949, 'update': '2022-03-18-16-40-05'}, {'id': 'CCTV22_2', 'top': 1421, 'left': 995, 'update': '2022-03-18-16-40-05'}]")