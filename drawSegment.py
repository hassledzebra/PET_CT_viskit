import cv2


import torch
import numpy as np
import os
from torch.utils.data import TensorDataset, DataLoader
import util

def path_prep_data(rootpath, patient_ID):
    patient_ID = str(patient_ID)
    
    idx_path = os.path.join(rootpath ,"p" + patient_ID + "t1", "p" + patient_ID + "t1ct1_raw")

    return idx_path

def click_event(event, x, y, flags, params):
 
    # checking for left mouse clicks
    if event == cv2.EVENT_LBUTTONDOWN:
 
        # displaying the coordinates
        # on the Shell
        print(x, ' ', y)
 
        # displaying the coordinates
        # on the image window
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(img, str(x) + ',' +
                    str(y), (x,y), font,
                    1, (255, 0, 0), 2)
        cv2.imshow('image', img)
 
    # checking for right mouse clicks    
    if event==cv2.EVENT_RBUTTONDOWN:
 
        # displaying the coordinates
        # on the Shell
        print(x, ' ', y)
 
        # displaying the coordinates
        # on the image window
        font = cv2.FONT_HERSHEY_SIMPLEX
        b = img[y, x, 0]
        g = img[y, x, 1]
        r = img[y, x, 2]
        cv2.putText(img, str(b) + ',' +
                    str(g) + ',' + str(r),
                    (x,y), font, 1,
                    (255, 255, 0), 2)
        cv2.imshow('image', img)
 
# driver function

 
# reading the image

patient_ID = 1
# patient_ID_list = [4,1,6,17]
rootpath = os.path.join(os.path.dirname(os.getcwd()),'python')

idx_path = path_prep_data(rootpath, patient_ID)
 
# path
path = idx_path+'.npy'

idx = np.load(idx_path + '.npy')

idx = idx > 200
 
# Reading an image in default
# mode
# image = idx

img = idx[:,:,0]
img = np.stack([img,img,img],2)
img = img.astype('float64')


ndarray = np.full((300,300,3), 125, dtype=np.uint8)

# displaying the image
cv2.imshow('image', img)

# setting mouse handler for the image
# and calling the click_event() function
cv2.setMouseCallback('image', click_event)

# wait for a key to be pressed to exit
cv2.waitKey(0)

# close the window
cv2.destroyAllWindows()

 
# Window name in which image is
# displayed
window_name = 'Image'
 
# Polygon corner points coordinates
pts = np.array([[25, 70], [25, 160],
                [110, 200], [200, 160],
                [200, 70], [110, 20]],
               np.int32)
 
pts = pts.reshape((-1, 1, 2))
 
isClosed = True
 
# Blue color in BGR
color = (255, 0, 0)
 
# Line thickness of 2 px
thickness = 2
 
# Using cv2.polylines() method
# Draw a Blue polygon with
# thickness of 1 px
image = cv2.polylines(image, [pts],
                      isClosed, color, thickness)
 
# Displaying the image
while(1):
     
    cv2.imshow('image', image)
    if cv2.waitKey(20) & 0xFF == 27:
        break
         
cv2.destroyAllWindows()