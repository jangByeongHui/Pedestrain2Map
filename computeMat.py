import cv2
import numpy as np

pts_src=np.float32([[1609,800],[994,236],[592,247],[111,694]]) #cctv
pts_dst=np.float32([[615,2238],[618,1697],[412,1688],[412,2182]]) #map

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

