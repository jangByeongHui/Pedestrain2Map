import cv2
import numpy as np

pts_src=np.float32([[1770,895],[1553,334],[1518,233],[1163,215],[707,353]]) #cctv
pts_dst=np.float32([[1905,832],[2200,1009],[2399,1173],[2401,953],[2141,753]]) #map

pts_src=np.array(pts_src)
pts_dst=np.array(pts_dst)


H, status = cv2.findHomography(pts_src, pts_dst)

H=list(H)
print("Found H Matrix")
for num,i in enumerate(H):
    temp = list(i)
    print("[",end="")
    print(temp[0],temp[1],temp[2],sep=", ",end="")
    if num==2:
        print("]",end="")
    else:
        print("],", end="")

