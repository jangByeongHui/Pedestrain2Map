# MQTTLens

import paho.mqtt.client as mqtt
import time
import multiprocessing
import keyboard

# data = [{'id': f'{cctv_name}_{num + 1}', 'top': y, 'left': x,'update': str(datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S'))}]
start_time = 0
end_time = 0
def put(data):
    global start_time
    try:
        topic='data'
        clientId="tester1"
        mqttHost="13.125.166.98"
        mqttPort=1883

        pubClt=mqtt.Client(clientId)
        pubClt.connect(mqttHost,mqttPort)


        pubClt.loop_start()
        start_time = time.process_time()
        pubClt.publish(topic,data,1)
        pubClt.loop_stop()
        print(f'Success publishing data')
    except Exception as e:
        print(f'failed publishing data: {e}')

def on_message(client, userdata, message):
    global start_time,end_time
    end_time =time.process_time()
    print("message received ", str(message.payload.decode("utf-8")))
    print("message topic=", message.topic)
    print("message qos=", message.qos)
    print("message retain flag=", message.retain)
    print(f'spend Time : {int(round((end_time - start_time) * 1000))}ms')


def sub():
    broker_address = "13.125.166.98"
    client2 = mqtt.Client("client2")
    client2.connect(broker_address)
    client2.subscribe("data")
    client2.on_message = on_message
    client2.loop_forever()

def send():
    while True:
        put("[{'id': 'CCTV20_1', 'top': 1805, 'left': 2438, 'update': '2022-03-18-16-40-05'}, {'id': 'CCTV21_1', 'top': 2305, 'left': 1221, 'update': '2022-03-18-16-40-05'}, {'id': 'CCTV22_1', 'top': 1390, 'left': 949, 'update': '2022-03-18-16-40-05'}, {'id': 'CCTV22_2', 'top': 1421, 'left': 995, 'update': '2022-03-18-16-40-05'}]")
        time.sleep(10)

if __name__ == '__main__':
    jobs = []
    p = multiprocessing.Process(target=sub,args=())
    p.start()
    jobs.append(p)
    p = multiprocessing.Process(target=send, args=())
    p.start()
    jobs.append(p)

    for proc in jobs:
        proc.join()