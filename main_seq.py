import cv2
import time
from config_hd_2 import cams
from transmit_server import put
import numpy as np
import torch
import datetime
import multiprocessing

def getFrame(cctv_addr,cctv_name,return_dict):
    font = cv2.FONT_HERSHEY_SIMPLEX  # 글씨 폰트
    cap = cv2.VideoCapture(cctv_addr)
    while True:
        ret,frame = cap.read()
        if ret:
            return_dict['img'][cctv_name] = frame
        else:
            Error_image = np.zeros((720, 1920, 3), np.uint8)
            cv2.putText(Error_image, "Video Not Found!", (20, 70), font, 1, (0, 0, 255), 3)  # 비디오 접속 끊어짐 표시
            return_dict['img'][cctv_name] = Error_image
            #retry
            cap = cv2.VideoCapture(cctv_addr)
        k = cv2.waitKey(1) & 0xff
        if k == 27:
            break



def detect(return_dict):
    font = cv2.FONT_HERSHEY_SIMPLEX  # 글씨 폰트
    # yolov5
    # yolov5
    # 로컬 레포에서 모델 로드(yolov5s.pt 가중치 사용, 추후 학습후 path에 변경할 가중치 경로 입력)
    # 깃허브에서 yolov5 레포에서 모델 로드
    # model = torch.hub.load('ultralytics/yolov5', 'custom', path='yolov5s.pt',device=num%3)
    model = torch.hub.load('yolov5', 'custom', path='yolov5s.pt', source='local', device=0)
    # 검출하고자 하는 객체는 사람이기 때문에 coco data에서 검출할 객체를 사람으로만 특정(yolov5s.pt 사용시)
    model.classes = [0]
    model.conf = 0.7
    while True:
        for cctv_name in cams.keys():
            # 추론
            img = return_dict['img'][cctv_name]
            bodys = model(img, size=640)

            flag = False
            points = []

            # yolo5
            for i in bodys.pandas().xyxy[0].values.tolist():

                # 결과
                x1, y1, x2, y2, conf, cls, name = int(i[0]), int(i[1]), int(i[2]), int(i[3]), i[4], i[5], i[6]

                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)  # bounding box
                cv2.putText(img, name, (x1 - 5, y1 - 5), font, 0.5, (255, 0, 0), 1)  # class 이름
                cv2.putText(img, "{:.2f}".format(conf), (x1 + 5, y1 - 5), font, 0.5, (255, 0, 0), 1)  # 정확도

                # 보행자 좌표 표시
                target_x = int((x1 + x2) / 2)  # 보행자 중심 x 좌표
                target_y = int(y2)  # 보행자 하단 좌표

                # 보행자 픽셀 위치 표시
                img = cv2.circle(img, (target_x, target_y), 10, (255, 0, 0), -1)
                cv2.putText(img, "X:{} y:{}".format(target_x + 5, target_y + 5), (target_x + 10, target_y + 10), font,
                            0.5, (255, 0, 255), 1)

                # homography 변환
                target_point = np.array([target_x, target_y, 1], dtype=int)
                target_point.T
                H = np.array(cams[cctv_name]['homoMat'])
                target_point = H @ target_point
                target_point = target_point / target_point[2]
                target_point = list(target_point)
                target_point[0] = round(int(target_point[0]), 0)  # x - > left
                target_point[1] = round(int(target_point[1]), 0)  # y - > top
                points.append((target_point[0], target_point[1]))
                flag = True  # 변환된 정보 저장

            # 변환된 보행자 픽셀 위치 저장
            if flag:
                return_dict[cctv_name] = (flag, points)
            else:
                return_dict[cctv_name] = (False, [])
            temp_img = cv2.resize(img, dsize=(720, 480))
            cv2.imshow(cctv_name, temp_img)

        send2server(return_dict)
        k = cv2.waitKey(1) & 0xff
        if k == 27:
            break



# 추후 서버 전송
# MQTT 전송시에는 데이터를 문자열로 보내야 한다.
def send2server(data):
    Map_path = "./data/B3.png"
    Map = cv2.imread(Map_path)
    try:
        temp_list = []
        state = False
        for cctv_name in cams.keys():
            flag, points = data[cctv_name]
            if flag:
                state = True
                for num, (x, y) in enumerate(points):
                    Map = cv2.circle(Map, (x, y), 30, (0, 255, 0), -1)  # 지도위에 표시
                    temp_list.append({'id': f'{cctv_name}_{num + 1}', 'top': y, 'left': x,
                                      'update': str(datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S'))})
        temp_Map = cv2.resize(Map, dsize=(720, 480))
        cv2.imshow("Map", temp_Map)
        if state:
            print(f'state:{state} data:{temp_list}')
            put(f'{temp_list}')
    except Exception as e:
        print(f'state:{state} data:{temp_list}')
        print("Send2Server Error : {}".format(e))
        pass


def main():
    # 작업 결과 저장 dict
    manager = multiprocessing.Manager()
    return_dict = manager.dict()
    return_dict['img'] = manager.dict()
    #init
    for cctv_name in cams.keys():
        return_dict['img'][cctv_name] = np.zeros((1080, 1920, 3), np.uint8)
    work_lists=[]
    jobs=[]

    for cctv_name in cams.keys():
        work_lists.append((cams[cctv_name]['src'],cctv_name,return_dict))

    for i,work in enumerate(work_lists):
        p = multiprocessing.Process(target=getFrame, args=work)
        jobs.append(p)
        p.start()
    else:
        p = multiprocessing.Process(target=detect, args=(return_dict,))
        jobs.append(p)
        p.start()

    for proc in jobs:
        proc.join()






        

if __name__ == '__main__':
    main()
