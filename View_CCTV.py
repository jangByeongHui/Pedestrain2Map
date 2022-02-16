import cv2
import numpy as np
import multiprocessing
from config_hd_2 import cams
import time
import pafy


def View_cam(cctv_name,cctv_addr):
    
    cap = cv2.VideoCapture(cctv_addr)
    
    while True:
        start_time  = time.time()
        ret,frame = cap.read()
        end_time = time.time()
        print(f'Get {cctv_name} frames - {round(end_time - start_time,3)} s')

        if ret:
            frame = cv2.resize(frame,dsize=(720,480))
            cv2.imshow(cctv_name,frame)
        else:
            Error_image = np.zeros((480, 720, 3), np.uint8)
            cv2.putText(Error_image, "Video Not Found!", (340, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)  # 비디오 접속 끊어짐 표시
            cv2.imshow(cctv_name, Error_image)
            cap = cv2.VideoCapture(cctv_addr)

        k = cv2.waitKey(1) & 0xff
        if k == 27:
            cap.release()
            break

def main(): 
    cctv_addrs=dict()
    works=[]
    jobs=[]
    video=pafy.new("https://www.youtube.com/watch?v=nzvaWlpEbnc")
    best=video.getbest(preftype="mp4")
    cctv_addrs['YTN']=best.url
    

    # for cctv_name in cams.keys():
    #     works.append((cctv_name,cams[cctv_name]['src']))
    for cctv_name in cctv_addrs:
        works.append((cctv_name,cctv_addrs[cctv_name]))

    for i, work in enumerate(works):
        p = multiprocessing.Process(target=View_cam, args=work)
        jobs.append(p)
        p.start()

    for proc in jobs:
        proc.join()


if __name__=='__main__':
    main()