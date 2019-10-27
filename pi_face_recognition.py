# Read the README.MD file for usage details
import face_recognition	#https://github.com/ageitgey/face_recognition using dlib #http://dlib.net
import argparse
import pickle	#https://docs.python.org/3/library/pickle.html
import time
import cv2
import pygame	#for playing audio files https://www.pygame.org/news

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-c", "--cascade", required=True,
	help = "path to where the face cascade resides")
ap.add_argument("-e", "--encodings", required=True,
	help="path to serialized db of facial encodings")
args = vars(ap.parse_args())

# load the known faces and embeddings along with OpenCV's Haar
# cascade for face detection
print("[INFO] loading encodings + face detector...")
data = pickle.loads(open(args["encodings"], "rb").read())
detector = cv2.CascadeClassifier(args["cascade"])

# initialize video stream (vs)
print("Starting video stream...")
vs=cv2.VideoCapture(0) #works for most devices, otherwise check with lsusb and devices in /dev/
vs.set(cv2.CAP_PROP_FRAME_WIDTH, 1280) # set the Horizontal resolution
vs.set(cv2.CAP_PROP_FRAME_HEIGHT, 720) # Set the Vertical resolution
vs.set(cv2.CAP_PROP_BRIGHTNESS,0.4)

#variables for checking if a person has already been greeted.
#otherwise a greeting would be played at every face recognition (while standing in the hallway for example)
alreadyGreetedMichael = False
alreadyGreetedEmanuela = False

side = "none"	#variable for setting the side of the door (left/right), in which the first movement was detected

#timestamp variables for checking which was first
leftSideTimestamp = 0
rightSideTimestamp = 0

#time.time() = floating point number expressed in seconds since the epoch, in UTC ! https://www.tutorialspoint.com/python/time_time.htm
infotimer = time.time()	#just an information for how long the camera has been running

#timer variables for each person living in the appartment.
#a person should not be greeted twice, usually a person will not leave and come home faster than in 2 minutes.
startTimerMichael = time.time()
startTimerEmanuela = time.time()

#read a frame (grab & retrieve), convert to gray, equalize, blur and resize
#for highest performance optimization. For more details see the paper.
def grab_resized_grey_blurred_frame(cap):
	ret = cap.grab()
	ret, frame = cap.retrieve()
	frame = cv2.resize(frame,(frame.shape[1]//2,frame.shape[0]//2))
	frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	cv2.equalizeHist(frame)
	frame = cv2.medianBlur(frame,3)
	return frame

#example from Mr. McGuire, the inital frame change detection
def detect_first_movement_side(frame, lframe):
	diff = cv2.addWeighted(lframe, 0.5, frame, -0.5, 0.0)	#calculates weighted sum of 2 frames
	d_hist = cv2.calcHist([diff],[0],None,[16],[0,256])
	if(d_hist[2] > 5):	#5 works best for movement detection, not to low, nor to high
		return True
	return False

#detect frame changes and on which side the first frame changed
def frameChanged(init_frame, curr_frame):   
	global side
	global leftSideTimestamp
	global rightSideTimestamp

	#split frame into left and right part
	#img sizes are globally defined and divded by 2 later => x=640,y=360)
	#left side is from 0 - 320 but the whole y from 0 - 360
	#right side is from 320 - 640 but the whole y from 0 - 360 
	leftSideMovement = detect_first_movement_side(init_frame[0:320, 0:360], curr_frame[0:320, 0:360])
	if leftSideMovement == True :
		leftSideTimestamp = time.time()
	rightSideMovement = detect_first_movement_side(init_frame[320:640, 0:360], curr_frame[320:640, 0:360])
	if rightSideMovement == True :
		rightSideTimestamp = time.time()

	#detect which frame changed first by comparing timestamps of last changed frame.
	#Not the best apporach for longer videos, but works for inital detection if
	#someone ist coming or leaving home.
	if leftSideTimestamp > rightSideTimestamp:
		side = "right"
	if leftSideTimestamp < rightSideTimestamp:
		side = "left"

	if rightSideMovement == True or leftSideMovement == True:
		return True

#detect faces, read them in rgb, compare them with the dataset, play audio on face detection.
#fires on first Motion detection.
def detect_faces_and_recgonize_known_face():
	global alreadyGreetedMichael
	global alreadyGreetedEmanuela
	global side

	ret = vs.grab()
	ret, frame = vs.retrieve()
	frame = cv2.resize(frame,(frame.shape[1]//2,frame.shape[0]//2))

	# detect faces in the frame
	rects = detector.detectMultiScale(frame, scaleFactor=1.1, 
		minNeighbors=5, minSize=(30, 30),
		flags=cv2.CASCADE_SCALE_IMAGE)

	#BGR to RGB (needed for face recognition)
	rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

	# OpenCV returns bounding box coordinates in (x, y, w, h) order
	# but we need them in (top, right, bottom, left) order, so we
	# need to do a bit of reordering
	boxes = [(y, x + w, y + h, x) for (x, y, w, h) in rects]

	# compute the facial embeddings for each face bounding box
	encodings = face_recognition.face_encodings(rgb, boxes)
	names = []

	# loop over the facial embeddings
	for encoding in encodings:
		# attempt to match each face in the input image to our known
		# encodings
		matches = face_recognition.compare_faces(data["encodings"],
			encoding)
		name = "Unknown"

		# check to see if we have found a match
		if True in matches:
			# find the indexes of all matched faces then initialize a
			# dictionary to count the total number of times each face
			# was matched
			matchedIdxs = [i for (i, b) in enumerate(matches) if b]
			counts = {}

			# loop over the matched indexes and maintain a count for
			# each recognized face face
			for i in matchedIdxs:
				name = data["names"][i]
				counts[name] = counts.get(name, 0) + 1

			# determine the recognized face with the largest number
			# of votes (note: in the event of an unlikely tie Python
			# will select first entry in the dictionary)
			name = max(counts, key=counts.get)

			#determine doorstatus for audiofiles
			if side == "left":
				doorstatus="welcomeHome"
			if side == "right":
				doorstatus="bye"

			#greet at recognition
			if name == 'michael' and alreadyGreetedMichael == False:
				pygame.mixer.init()
				pygame.mixer.music.load("audioFiles/"+doorstatus+name+".wav")
				pygame.mixer.music.play()
				alreadyGreetedMichael=True
				starttimer(name)

				while pygame.mixer.music.get_busy() == True:
					continue

			if name == 'emanuela' and alreadyGreetedEmanuela == False:
				pygame.mixer.init()
				pygame.mixer.music.load("audioFiles/"+doorstatus+name+".wav")
				pygame.mixer.music.play()
				alreadyGreetedEmanuela=True
				starttimer(name)

				while pygame.mixer.music.get_busy() == True:
					continue
		
		# update the list of names
		names.append(name)

	# loop over the recognized faces
	for ((top, right, bottom, left), name) in zip(boxes, names):
		# draw the predicted face name on the image
		cv2.rectangle(frame, (left, top), (right, bottom),
			(0, 255, 0), 2)
		y = top - 15 if top - 15 > 15 else top + 15
		cv2.putText(frame, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX,
			0.75, (0, 255, 0), 2)

	# display the image
	cv2.imshow("Frame", frame)

#timer for not greeting at every face recognition.
#timeout set to 2 minutes, so only every 2 minutes a greeting will be played.
#split per person.
def starttimer(name):
	global alreadyGreetedMichael
	global alreadyGreetedEmanuela
	global startTimerMichael
	global startTimerEmanuela

	if name == "michael":
		curr=time.time()
		diff=curr-startTimerMichael
		if diff > 120:
			startTimerMichael=time.time()
			alreadyGreetedMichael=False
	if name == "emanuela":
		curr=time.time()
		diff=curr-startTimerEmanuela
		if diff > 120:
			startTimerEmanuela=time.time()
			alreadyGreetedEmanuela=False

#'main' from here

#get initial frame
initialFrame = grab_resized_grey_blurred_frame(vs)

#loop over frames from the video file stream
while True:
	
	frame = grab_resized_grey_blurred_frame(vs)
	if frameChanged(initialFrame, frame):
		print("Motion detected on the "+side+" side of the door")
		detect_faces_and_recgonize_known_face() #since face recognition most power expensive, only start at motion detection.

	key = cv2.waitKey(1) 
	if key == ord("q"):
		break

infotimer=int(time.time()-infotimer)
print("Stream was activated for "+str(infotimer)+" seconds")

vs.release()
cv2.destroyAllWindows()