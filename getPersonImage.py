import cv2
import datetime
import multiprocessing
from config_hd_2 import cams
import torch

def writeVideo(Rtsp_addr,cctv_name,num):
    currentTime = datetime.datetime.now()
    video_capture = cv2.VideoCapture(Rtsp_addr)

    font = cv2.FONT_HERSHEY_SIMPLEX  # 글씨 폰트

    fps = 20
    video_capture.set(3,1280)
    video_capture.set(4,720)

    streaming_window_width = int(video_capture.get(3))
    streaming_window_height = int(video_capture.get(4))  
    
   
    fileName = "{}_{}".format(cctv_name,str(currentTime.strftime('%Y_%m _%d_%H_%M_%S')))

  
    path = './CCTV_Person/{}.mp4'.format(fileName)
    

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')


    out = cv2.VideoWriter(path, fourcc, fps, (streaming_window_width, streaming_window_height))

    #yolov5
    model = torch.hub.load('/home/ves/yolov5', 'custom', path='yolov5s.pt', source='local', device=num % 3)
    model.classes = [0]
    model.conf=0.7

    while True:
        ret, frame = video_capture.read()
        person_found=False
        if ret:
            # yolo5
            bodys = model(frame, size=640)
            for i in bodys.pandas().xyxy[0].values.tolist():

                # 결과
                x1, y1, x2, y2, conf, cls, name = int(i[0]), int(i[1]), int(i[2]), int(i[3]), i[4], i[5], i[6]

                #bounding box
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)  # bounding box
                cv2.putText(frame, name, (x1 - 5, y1 - 5), font, 0.5, (255, 0, 0), 1)  # class 이름
                cv2.putText(frame, "{:.2f}".format(conf), (x1 + 5, y1 - 5), font, 0.5, (255, 0, 0), 1)  # 정확도

                # 보행자 좌표 표시
                target_x = int((x1 + x2) / 2)  # 보행자 중심 x 좌표
                target_y = int(y2)  # 보행자 하단 좌표

                # 보행자 픽셀 위치 표시
                frame = cv2.circle(frame, (target_x, target_y), 10, (255, 0, 0), -1)
                cv2.putText(frame, "X:{} y:{}".format(target_x + 5, target_y + 5), (target_x + 10, target_y + 10), font, 0.5,
                            (255, 0, 255), 1)
                cv2.imwrite(f"./CCTV_Person/{cctv_name}/{cctv_name}_{str(datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S'))}.jpg",frame)
                out.write(frame)
                person_found=True

            temp_frame=cv2.resize(frame,dsize=(300,150))
            if person_found:
                cv2.putText(temp_frame, "PersonDetect!", (30, 70), font, 1, (0, 0, 255), 3)  # 감지 표시
            cv2.imshow(cctv_name, temp_frame)
        else:
            #비디오 못찾으면 재연결 시도
            print(f'{cctv_name}:{Rtsp_addr} Not Found retry Reload')
            video_capture = cv2.VideoCapture(Rtsp_addr)
            video_capture.set(3, 1280)
            video_capture.set(4, 720)
            streaming_window_width = int(video_capture.get(3))
            streaming_window_height = int(video_capture.get(4))
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(path, fourcc, fps, (streaming_window_width, streaming_window_height))


        
        # ESC 누를시 종료
        k = cv2.waitKey(1) & 0xff

        if k == 27:
            break
    video_capture.release() 
    out.release()  
    cv2.destroyAllWindows()

if __name__ == "__main__":
    works=[]
    jobs=[]
    Rtsp=["rtsp://1.255.252.7:505/live_1","rtsp://1.255.252.7:505/live_2","rtsp://1.255.252.7:505/live_3","rtsp://1.255.252.7:505/live_4","rtsp://1.255.252.7:505/live_5","rtsp://1.255.252.7:505/live_6"
          ,"rtsp://1.255.252.7:505/live_7","rtsp://1.255.252.7:505/live_8","rtsp://1.255.252.7:505/live_9","rtsp://1.255.252.7:505/live_10","rtsp://1.255.252.7:505/live_11","rtsp://1.255.252.7:505/live_12"
          ,"rtsp://1.255.252.7:505/live_13","rtsp://1.255.252.7:505/live_14","rtsp://1.255.252.7:505/live_15","rtsp://1.255.252.7:505/live_16","rtsp://1.255.252.7:505/live_17","rtsp://1.255.252.7:505/live_18"]
    # 병렬 실행할 work 생성
    for num,cctv_name in enumerate(list(cams.keys())[0:18]):
        works.append((Rtsp[num],cctv_name,num))

    #병렬 실행
    for num,work in enumerate(works):
        p=multiprocessing.Process(target=writeVideo, args=work)
        jobs.append(p)
        p.start()

    #생성 프로세스 join
    for proc in jobs:
        proc.join()
