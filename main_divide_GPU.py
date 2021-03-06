import cv2
import time
from config_hd_2 import cams
from transmit_server import put
import multiprocessing
import numpy as np
import torch
import datetime
from math import ceil
# import csv

def multidetect(cctv_names,return_dict,num):

    font = cv2.FONT_HERSHEY_SIMPLEX # 글씨 폰트

    #yolov5
    # 로컬 레포에서 모델 로드(yolov5s.pt 가중치 사용, 추후 학습후 path에 변경할 가중치 경로 입력)
    model = torch.hub.load('/home/ves/yolov5', 'custom', path='yolov5s.pt',source='local',device=num)
    # 깃허브에서 yolov5 레포에서 모델 로드
    #model = torch.hub.load('ultralytics/yolov5', 'custom', path='yolov5s.pt',device=num%3)

    #검출하고자 하는 객체는 사람이기 때문에 coco data에서 검출할 객체를 사람으로만 특정(yolov5s.pt 사용시)
    model.classes=[0]
    model.conf=0.7

    # 동영상 혹은 실시간 영상 캡쳐
    caps = dict()
    for cctv_name in cctv_names:
        caps[cctv_name]=cv2.VideoCapture(cams[cctv_name]['src'])
    # 결과 저장할 경로
    #path = "./runs/{}.mp4".format(cctv_name)
    # 코덱 설정
    #fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    #out = cv2.VideoWriter(path,fourcc,30,(int(cap.get(3)),int(cap.get(4))))
    while True:
        # startTime = time.time()
        #프레임 가져오기
        for cctv_name in cctv_names:
            ret,img=caps[cctv_name].read()
            addr = cams[cctv_name]['src']
            homoMat = cams[cctv_name]['homoMat']
            if ret:
                #yolov5
                # 추론
                bodys=model(img,size=640)

                flag=False
                points=[]

                #yolo5
                for i in bodys.pandas().xyxy[0].values.tolist():
                    # f.write("Video({}) found\n".format(cctv_name))
                    # f.write("{}\n".format(i))

                    # 결과
                    x1,y1,x2,y2,conf,cls,name=int(i[0]),int(i[1]),int(i[2]),int(i[3]),i[4],i[5],i[6]

                    cv2.rectangle(img,(x1,y1),(x2,y2),(0,255,0),2) # bounding box
                    cv2.putText(img,name,(x1-5,y1-5),font,0.5,(255,0,0),1) # class 이름
                    cv2.putText(img,"{:.2f}".format(conf), (x1+5, y1 - 5), font, 0.5, (255, 0, 0), 1) #정확도

                    # 보행자 좌표 표시
                    target_x=int((x1+x2)/2) # 보행자 중심 x 좌표
                    target_y=int(y2) # 보행자 하단 좌표

                    # 보행자 픽셀 위치 표시
                    img=cv2.circle(img,(target_x,target_y),10,(255,0,0),-1)
                    cv2.putText(img,"X:{} y:{}".format(target_x+5,target_y+5),(target_x+10,target_y+10),font,0.5,(255,0,255),1)

                    # homography 변환
                    target_point = np.array([target_x, target_y, 1], dtype=int)
                    target_point.T
                    H=np.array(homoMat)
                    target_point=H@target_point
                    target_point=target_point/target_point[2]
                    target_point=list(target_point)
                    target_point[0]=round(int(target_point[0]), 0) # x - > left
                    target_point[1]=round(int(target_point[1]), 0) # y - > top
                    points.append((target_point[0],target_point[1]))
                    flag=True # 변환된 정보 저장

                # 변환된 보행자 픽셀 위치 저장
                if flag:
                    return_dict[cctv_name]=(flag,points)
                else:
                    return_dict[cctv_name]=(flag,[])
                temp_img = cv2.resize(img, dsize=(300, 180))
                cv2.imshow(cctv_name, temp_img)

                #비디오 저장
                # out.write(img)
                # endTime=time.time()

                # print("MultiProcess({}):{:.3f}s\n".format(cctv_name,endTime-startTime))
                # f.write("{} MultiProcess({}):{:.3f}s\n".format(datetime.datetime.now(),cctv_name,endTime-startTime))
                # with open('result.csv', 'a', encoding='utf-8', newline='') as f:
                #     wr =csv.writer(f)
                #     wr.writerow([datetime,cctv_name,endTime-startTime,len(bodys.pandas().xyxy[0].values.tolist())])

            else:
                return_dict[cctv_name] = (False, [])
                print("Video({}) Not found".format(cctv_name))
                Error_image = np.zeros((180, 300, 3), np.uint8)
                cv2.putText(Error_image, "Video Not Found!", (20, 70), font, 1, (0, 0, 255), 3)  # 비디오 접속 끊어짐 표시
                cv2.imshow(cctv_name, Error_image)
                # f.write("{} Video({}) Not found\n".format(datetime.datetime.now(),cctv_name))
                caps[cctv_name].release()
                # break
                caps[cctv_name] = cv2.VideoCapture(addr)
            #ESC 누를 시 종료
            k = cv2.waitKey(1) & 0xff
            if k == 27:
                caps[cctv_name].release()
                # out.release()
                break

def show_image(return_dict):

    Map_path = "./data/B3.png"
    path = "./runs/Map.mp4"
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(path, fourcc, 30, (1280,720))
    while True:
        # startTime = time.time()
        Map = cv2.imread(Map_path)
        try:
            send2server(return_dict,Map,out) #지도 표시전 서버에 보행자 위치 전송 및 지도 표시
        except:
            pass
        # stopTime = time.time()
        #print("View All result:{:.3f}s".format(stopTime - startTime))
        # ESC 누를 시 종료
        k = cv2.waitKey(1) & 0xff
        if k == 27:
            # out.release()
            break

#추후 서버 전송
#MQTT 전송시에는 데이터를 문자열로 보내야 한다.
def send2server(data,Map,out):
    try:
        temp_list=[]
        state=False
        for cctv_name in data.keys():
            flag,points=data[cctv_name]
            if flag:
                state=True
                for num,(x,y) in enumerate(points):
                    Map = cv2.circle(Map, (x, y), 30, (0, 255, 0), -1)  # 지도위에 표시
                    temp_list.append({'id':f'{cctv_name}_{num+1}','top':y,'left':x,'update':str(datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S'))})
        temp_Map = cv2.resize(Map, dsize=(720, 480))
        cv2.imshow("Map", temp_Map)
        # out.write(temp_Map)

        if state:
            print(f'state:{state} data:{temp_list}')
            put(f'{temp_list}')
    except Exception as e:
        print("Send2Server Error : {}".format(e))
        pass


def main():
    # RTSP Test 영상
    #Rtsp=["./data/Anyang2_SKV1_ch1_20220121090906.mp4","./data/Anyang2_SKV1_ch2_20220126165051_20220126165101.mp4","./data/Anyang2_SKV1_ch3_20220126165125_20220126165210.mp4"]
    # Rtsp=["./data/Anyang2_SKV1_ch1_20220121090906.mp4","./data/Anyang2_SKV1_ch2_20220126165051_20220126165101.mp4","./data/Anyang2_SKV1_ch3_20220126165125_20220126165210.mp4","data/Anyang2_SKV1_ch4_20220124132217_20220124132240.mp4","data/Anyang2_SKV1_ch5_20220126165037_20220126165047.mp4"]
    #작업 결과 저장 dict
    manager = multiprocessing.Manager()
    return_dict = manager.dict()
    NumOfGPU = 4
    len_addrs = len(cams.keys())
    perAddrs = int(ceil(len_addrs/NumOfGPU))
    cctv_names = list(cams.keys())
    #프로세스 작업 리스트
    work_list = []
    for i in range(NumOfGPU-1):
        work_list.append((cctv_names[i*perAddrs : i*perAddrs+perAddrs], return_dict, i))  # config_hd_2에 정의된 주소
    else:
        work_list.append((cctv_names[i * perAddrs+perAddrs : -1], return_dict, i))  # config_hd_2에 정의된 주소
    # 멀티 프로세싱을 위한 작업 아규먼트 값
    # for num,cctv_name in enumerate(cams.keys()):
    #     work_list.append((cams[cctv_name]['src'],cctv_name,cams[cctv_name]['homoMat'],return_dict,num)) # config_hd_2에 정의된 주소
    #     #work_list.append((Rtsp[num], cctv_name, cams[cctv_name]['homoMat'], return_dict, num)) # 테스트 주소

    # 병렬 프로세스 실행
    jobs=[]

    for i,work in enumerate(work_list):
        p = multiprocessing.Process(target=multidetect, args=work)
        jobs.append(p)
        p.start()

    else:
        p=multiprocessing.Process(target=show_image, args=(return_dict,))
        jobs.append(p)
        p.start()

    for proc in jobs:
        proc.join()
    stopTime = time.time()

    #병렬 프로세스 실행 끝
    # k = cv2.waitKey(1) & 0xff
    # if k == 27:
    #     break

    cv2.destroyAllWindows()

if __name__=='__main__':
    main()
    