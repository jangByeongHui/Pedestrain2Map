import cv2
import numpy as np

pts_src=np.float32([[1669,520],[1331,228],[885,209],[662,465],[1096,455]]) #cctv
pts_dst=np.float32([[1511,1186],[1307,1188],[1311,1301],[1509,1301],[1502,1234]]) #map

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

