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
    count = 0
    while True:
        put("#"+str(count+1))
        count += 1
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

