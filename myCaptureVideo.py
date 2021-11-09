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
    frame=cv2.medianBlur(frame,5)
    #threshold
    #frame=cv2.adaptiveThreshold(frame,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY_INV,45,0)
    #thresh 2
    thresh = cv2.threshold(frame, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

    # Close contour
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (7,7))
    close = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=1)

    # Find outer contour and fill with white
    cnts = cv2.findContours(close, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    cv2.fillPoly(close, cnts, [255,255,255])
    
    frame=close

    #save frame
    lframe=frame

    #read new frame
    ret,frame=cap.read()
    frame=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
    frame=frame[::2,::2]
    frame=cv2.medianBlur(frame,5)

    #threshold
    #frame=cv2.adaptiveThreshold(frame,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY_INV,45,0)
    #thresh 2
    thresh = cv2.threshold(frame, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

    # Close contour
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (7,7))
    close = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=1)

    # Find outer contour and fill with white
    cnts = cv2.findContours(close, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    cv2.fillPoly(close, cnts, [255,255,255])

    frame=close
    #create diff
    diff=lframe-frame

    cv2.imshow("USB0",diff)
    key=cv2.waitKey(200)

    if key==ord("q"):
        break;

cv2.destroyAllWindows()
cap.release()
