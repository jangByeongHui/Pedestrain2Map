# MQTTLens

import paho.mqtt.client as mqtt

def put(data):
    try:
        topic='wm'
        clientId=""
        mqttHost="13.125.166.98"
        mqttPort=1883

        pubClt=mqtt.Client(clientId)
        pubClt.connect(mqttHost,mqttPort)

        pubClt.loop_start()
        pubClt.publish(topic,data,1)
        pubClt.loop_stop()
    except:
        print(f'failed publishing data:{data}')