import cv2
import numpy as np

pts_src=np.float32([[1269,605],[42,442],[17,712],[1261,709]]) #cctv
pts_dst=np.float32([[1100,1946],[615,1954],[945,2147],[1078,2079]]) #map

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

