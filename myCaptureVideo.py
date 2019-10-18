#! /usr/bin/env python3
import cv2
import numpy

cap=cv2.VideoCapture(0)

while cap.isOpened():
	#read input
	ret,frame=cap.read()
	
	#grayscale
	frame=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
	#resize
	frame=frame[::2,::2]
	#blur
	frame=cv2.medianBlur(frame,3)

	#save frame
	lframe=frame

	#read new frame
	ret,frame=cap.read()
	frame=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
	frame=frame[::2,::2]
	frame=cv2.medianBlur(frame,3)

	#create diff
	diff=lframe-frame
	
	cv2.imshow("USB0",diff)
	key=cv2.waitKey(200)
	
	if key==ord("q"):
		break;

cv2.destroyAllWindows()
cap.release()
