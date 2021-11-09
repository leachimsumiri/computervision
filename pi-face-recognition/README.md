USAGE

create a dataset with min. 5 pictures of a person (pics inside ./dataset/%PERSONNAME%/)

install python libraries (python 3 needed!):
* pip3 install opencv
* pip3 install pygame
* pip3 install face-recognition
* pip3 install dlib

encode a given dataset with given encodings 
- python3 encode_faces.py --dataset dataset --encodings encodings.pickle --detection-method hog
	- cnn for strong pcs with GPU's
	- hog elsewhere (raspberry pi etc.)

connect a camera and a speaker if you are on a raspberry

start the stream on a pc
- python3 recognize_faces_video.py --encodings encodings.pickle --output output/webcam_face_recognition_output.avi --display 1

start the stream including OpenCV Haar Cascade for better performance and the previoulsy generated encodings
- python3 pi_face_recognition.py --cascade haarcascade_frontalface_default.xml --encodings encodings.pickle
