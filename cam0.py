cap = cv2.VideoCapture(0)
while(cap.isOpened()): 
   ret, frame = cap.read()
   cv2.imshow('USB0-frame', frame)
   key = cv2.waitKey(300)
   if key == ord('q'):
      break

cap.release()
cv2.destroyWindow('USB0-frame')