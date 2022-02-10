import cv2
import numpy as np

pts_src=np.float32([[1605,814],[163,789],[547,368],[1256,374],[927,495]]) #cctv
pts_dst=np.float32([[1014,1301],[1017,1188],[1164,1182],[1143,1303],[1098,1248]]) #map

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

