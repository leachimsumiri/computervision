#! /usr/bin/env python3

import cv2
#import matplotlib.pyplot as plt

def setup_camera(cid):
    """ setup capture device and set properties """
    cap = cv2.VideoCapture(cid)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280) # set the Horizontal resolution
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720) # Set the Vertical resolution
    cap.set(cv2.CAP_PROP_BRIGHTNESS,0.4)
    return cap

def grab_resized_frame(cap):
    """ grab a frame resize, equalize and blur it """
    ret = cap.grab()
    ret, frame = cap.retrieve()
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    cv2.equalizeHist(frame)
    frame = cv2.medianBlur(frame,3)
    frame = cv2.resize(frame,(frame.shape[1]//2,frame.shape[0]//2))
    return frame

def frameTriggert(frame, lframe):   
    """ trigger if anything significantly changed """
    diff = cv2.addWeighted(lframe, 0.5, frame, -0.5, 0.0)
    d_hist = cv2.calcHist([diff],[0],None,[16],[0,256])
    # just for curiosity
    # print(d_hist[:4])
    #
    # somewhat crude detector - if there are significant
    # amounts of non-black pixels assume something just
    # changed the image and record it.
    if(d_hist[2] > 5):
        return True
    return False

frame_count = 0
cap = setup_camera(0)

# get initial frame
frame = grab_resized_frame(cap)
while(cap.isOpened()): 
   lframe = frame # last frame against which we compare
   frame = grab_resized_frame(cap)
   if(frameTriggert(frame, lframe)):
       #cv2.imwrite("./images_detect8/detect%d.png" % frame_count, frame)
       frame_count += 1
   #wait for 300 milliseconds for key input to terminate loop
   cv2.imshow("USB0", frame)
   key = cv2.waitKey(4)
   if key == ord('q'):   
      break

cap.release()
cv2.destroyWindow('USB0-frame')
