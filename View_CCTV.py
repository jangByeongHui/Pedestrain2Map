import cv2
import numpy as np
import multiprocessing
from config_hd_2 import cams

def View_cam(cctv_name,cctv_addr):
    cap = cv2.VideoCapture(cctv_addr)
    print(f'CCTV : {cctv_name} now FPS{cap.get(cv2.CAP_PROP_FPS)}')
    cap.set(cv2.CAP_PROP_FPS,1)
    print(f'CCTV : {cctv_name} after set FPS{cap.get(cv2.CAP_PROP_FPS)}')
    while True:
        ret,frame = cap.read()

        if ret:
            frame = cv2.resize(frame,dsize=(1280,720))
            cv2.imshow(cctv_name,frame)
        else:
            Error_image = np.zeros((720, 1280, 3), np.uint8)
            cv2.putText(Error_image, "Video Not Found!", (0, 310), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)  # 비디오 접속 끊어짐 표시
            cv2.imshow(cctv_name, Error_image)

        k = cv2.waitKey(1) & 0xff
        if k == 27:
            cap.release()
            break

def main():
    works=[]
    jobs=[]

    for cctv_name in cams.keys():
        works.append((cctv_name,cams[cctv_name]['src']))

    for i, work in enumerate(works):
        p = multiprocessing.Process(target=View_cam, args=work)
        jobs.append(p)
        p.start()

    for proc in jobs:
        proc.join()


if __name__=='__main__':
    main()