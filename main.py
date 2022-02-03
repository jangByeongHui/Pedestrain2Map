import cv2
import time
from config_hd_2 import cams
import multiprocessing
import numpy as np
import torch
import datetime

def multidetect(addr,cctv_name,homoMat,return_dict):
    f = open('result{}.txt'.format(cctv_name), 'a')
    font = cv2.FONT_HERSHEY_SIMPLEX
    #yolov5
    model = torch.hub.load('ultralytics/yolov5', 'custom', path='yolov5s.pt')
    model.classes=[0]


    cap=cv2.VideoCapture(addr)
    path = "./runs/{}.mp4".format(cctv_name)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(path,fourcc,30,(int(cap.get(3)),int(cap.get(4))))
    while True:
        startTime = time.time()
        #프레임 가져오기
        ret,img=cap.read()
        if ret:

            #yolov5
            bodys=model(img,size=640)

            flag=False
            points=[]

            #yolo5
            for i in bodys.pandas().xyxy[0].values.tolist():
                f.write("Video({}) found\n".format(cctv_name))
                f.write("{}\n".format(i))
                x1,y1,x2,y2,conf,cls,name=int(i[0]),int(i[1]),int(i[2]),int(i[3]),i[4],i[5],i[6]

                cv2.rectangle(img,(x1,y1),(x2,y2),(0,255,0),2)
                cv2.putText(img,i[6],(x1-5,y1-5),font,0.5,(255,0,0),1)
                cv2.putText(img,"{:.2f}".format(conf), (x1+5, y1 - 5), font, 0.5, (255, 0, 0), 1)
                # 보행자 좌표 표시
                target_x=int((x1+x2)/2)
                target_y=int(y2)
                img=cv2.circle(img,(target_x,target_y),10,(255,0,0),-1)
                cv2.putText(img,"X:{} y:{}".format(target_x+5,target_y+5),(target_x+10,target_y+10),font,0.5,(255,0,255),1)

                target_point = np.array([target_x, target_y, 1], dtype=int)
                target_point.T
                H=np.array(homoMat)
                target_point=H@target_point
                target_point=target_point/target_point[2]
                target_point=list(target_point)
                target_point[0]=round(int(target_point[0]), 0)
                target_point[1]=round(int(target_point[1]), 0)
                points.append((target_point[0],target_point[1]))
                flag=True
            # 영상을 저장한다.
            if flag:
                return_dict[cctv_name]=(flag,points)
            else:
                return_dict[cctv_name]=(flag,(0,0))
            temp_img = cv2.resize(img, dsize=(300, 180))
            cv2.imshow(cctv_name, temp_img)
            #비디오 저장
            out.write(img)
            endTime=time.time()
            print("MultiProcess({}):{:.3f}s\n".format(cctv_name,endTime-startTime))
            f.write("{} MultiProcess({}):{:.3f}s\n".format(datetime.datetime.now(),cctv_name,endTime-startTime))
        else:
            print("Video({}) Not found".format(cctv_name))
            f.write("{} Video({}) Not found\n".format(datetime.datetime.now(),cctv_name))
            cap.release()
            out.release()
            break
            #cap = cv2.VideoCapture(addr)
            #time.sleep(10)
        #ESC 누를 시 종료
        k = cv2.waitKey(1) & 0xff
        if k == 27:
            cap.release()
            out.release()
            break

def show_image(return_dict):

    Map_path = "./data/Anyang_B3.png"
    path = "./runs/Map.mp4"
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(path, fourcc, 30, (1280,720))
    while True:
        startTime = time.time()
        Map = cv2.imread(Map_path)
        try:
            for i in return_dict.keys():
                flag, points= return_dict[i]
                if flag:
                    for (x, y) in points:
                        Map = cv2.circle(Map, (x, y), 10, (0, 255, 0), -1)
            temp_Map = cv2.resize(Map, dsize=(1280, 720))
            cv2.imshow("Map", temp_Map)
            out.write(temp_Map)
        except:
            pass
        stopTime = time.time()
        #print("View All result:{:.3f}s".format(stopTime - startTime))
        # ESC 누를 시 종료
        k = cv2.waitKey(1) & 0xff
        if k == 27:
            out.release()
            break

def main():
    # RTSP 주소 모음
    #Rtsp = ["rtsp://admin:a1234567@1.255.252.7:500/cam/realmonitor?channel=1&subtype=0","rtsp://admin:a1234567@1.255.252.7:500/cam/realmonitor?channel=2&subtype=0","rtsp://admin:a1234567@1.255.252.7:500/cam/realmonitor?channel=3&subtype=0","rtsp://admin:a1234567@1.255.252.7:500/cam/realmonitor?channel=4&subtype=0","rtsp://admin:a1234567@1.255.252.7:500/cam/realmonitor?channel=5&subtype=0"]
    Rtsp=["./data/Anyang2_SKV1_ch1_20220121090906.mp4","./data/Anyang2_SKV1_ch2_20220126165051_20220126165101.mp4","./data/Anyang2_SKV1_ch3_20220126165125_20220126165210.mp4","./data/Anyang2_SKV1_ch4_20220124132217_20220124132240.mp4","./data/Anyang2_SKV1_ch5_20220126165037_20220126165047.mp4"]

    #작업 결과 저장 dict
    manager = multiprocessing.Manager()
    return_dict = manager.dict()

    #프로세스 작업 리스트
    work_list=[]
    # 멀티 프로세싱을 위한 작업 아규먼트 값
    for num,cctv_name in enumerate(cams.keys()):
        work_list.append((Rtsp[num],cctv_name,cams[cctv_name]['homoMat'],return_dict))

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
    