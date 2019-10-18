#!/usr/bin/env python3

"""take image of high and low-resolution camera and merge
   a small view of the low-resolution camera into the image
   of the high-res camera for position tracking (statically
   at 0,0 for now) - allow rotating (l=left,r=right) the
   image as well as zooming (i=in,o=out) and saving it
   with s - note that x and y seem to be swapped in the
   high-res camera...a bit confusing (atleast to me)"""

import cv2

def Rot(frame, deg):
   """ rotat fram deg returning rotated frame """
   width = frame.shape[1]
   height = frame.shape[0]
   M = cv2.getRotationMatrix2D((width/2,height/2),rot ,1)
   rot_frame = cv2.warpAffine(frame,M,(width,height))
   return rot_frame

def Zoom(frame, zoomSize):
   """ zoom around center of image """
   c_x = frame.shape[0]/2
   c_y = frame.shape[1]/2
   w_x = c_x/zoomSize
   w_y = c_y/zoomSize
   frame = frame[int(c_x-w_x):int(c_x + w_x), int(c_y-w_y):int(c_y+w_y)]
   frame = cv2.resize(frame,((int(frame.shape[0]*zoomSize)),
                             (int(frame.shape[1]*zoomSize))))
   return frame 

def SubFrame(frame, x, y):
   """ brute force subframing """
   c_x = frame.shape[0]/2
   c_y = frame.shape[1]/2
   frame = frame[int(c_x-x):int(c_x + x), int(c_y-y):int(c_y+y)]
   return frame 

def AddSubFrame(f,s,x,y):
   """ merge two frams """
   #offset should be checked - and there is some
   #problem with the offsets derived from shape
   #moving in y direction works - in x it fails
   #so some stupid bug here...
   f[x+0:x+s.shape[0], y+0:y+s.shape[1]] = s
   return f

rot=0
zoom_factor=1.0

#low-res camera
lcap = cv2.VideoCapture(0)
#High-res camera
hcap = cv2.VideoCapture(2)
# try setting to higher resolution
hcap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280) # set the Horizontal resolution
hcap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720) # Set the Vertical resolution
_ = hcap.set(cv2.CAP_PROP_BRIGHTNESS,0.4)

sat = 0.1
frame_count = 0

while(hcap.isOpened() & lcap.isOpened()): 
   # grab the frmae with grab/retrieve so we can connect multiple
   # cameras and get roughly synchronized imnages
   ret = hcap.grab()
   ret, frame = hcap.retrieve()
   ret = lcap.grab()
   ret, lframe = lcap.retrieve()
   # preprocess before storing
   rot_frame = Rot(frame, rot)
   zoom_frame = Zoom(rot_frame, zoom_factor)
   frame = AddSubFrame(zoom_frame, 
                       SubFrame(lframe, 50, 50),
                       0, 0)
   cv2.imshow('USB0-frame', frame)
   # image "control" - note that only the main frame is modified
   # the position subframe does not change.
   key = cv2.waitKey()
   if key != ord('q'):
      if key == ord('l'):
         rot += 2.5
      if key == ord('r'):
         rot -= 2.5
      if key == ord('i'):
         zoom_factor *= 1.05 if zoom_factor < 10.0 else 1.0
      if key == ord('o'):
         zoom_factor *= (1.0/1.05) if zoom_factor > 1.0 else 1.0
      if key == ord('+'):
         sat += 0.05 if sat < 1.0 else 0.0
      if key == ord('-'):
         sat -= 0.05 if sat > 0.0 else 0.0
      if key == ord('s'):
         cv2.imwrite("frame_base%d.jpg" % frame_count, frame)
         frame_count += 1
      continue
   else:
      break

hcap.release()
lcap.release()
cv2.destroyWindow('USB0-frame')
