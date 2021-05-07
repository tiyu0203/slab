from imutils.video import VideoStream
import imutils
import time
import cv2
from collections import deque 
import numpy as np
from pid import PID
from motor import Controller 
import sys

# https://en.wikipedia.org/wiki/PID_controller#Pseudocode
# https://sci-hub.scihubtw.tw/10.1109/ICETC.2010.5529177
# https://sci-hub.scihubtw.tw/10.1109/icsengt.2017.8123449
face_cascade = cv2.CascadeClassifier()
face_cascade.load(cv2.samples.findFile('venv/lib64/python3.9/site-packages/cv2/data/haarcascade_frontalface_alt.xml'))

Mx = PID()
My = PID()

controller = Controller(sys.argv[1])

print("[INFO] starting video stream...")
vs = VideoStream(src=0).start()
time.sleep(1.0)

def detectAndDisplay(frame):
	frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	frame_gray = cv2.equalizeHist(frame_gray)
	
	faces = face_cascade.detectMultiScale(frame_gray)
	amax = 0
	imax = None
	for i, (x,y,w,h) in enumerate(faces):
		a = w * h
		if a > amax:
			amax = a
			imax = i
		center = (x + w//2, y + h//2)
		frame = cv2.rectangle(frame, (x,y), (x+w,y+h), (255, 0, 255), 4)
	
	if imax is not None:
		(x,y,w,h) = faces[i];
		center = (x + w//2, y + h//2)
		frame = cv2.ellipse(frame, center, (w//2, h//2), 0, 0, 360, (0, 255, 0), 4)
	
	return frame, faces

def computeCenter(frame, box):
	(x,y,w,h) = box
	face_center = (x + w//2, y + h//2)
	(Dx, Dy) = tuple(np.subtract(frame_center, face_center))
	cv2.arrowedLine(frame, face_center, frame_center, (0,255,0),3,8,0,0.1)
	return Dx, Dy, frame

while True:
	frame = vs.read()
	if frame is None:
		break;
	
	frame = imutils.resize(frame, width=600)
	frame, faces = detectAndDisplay(frame)
	
	frame_center = frame.shape[1]//2, frame.shape[0]//2
	cv2.circle(frame,frame_center,4,(0,0,255),6)
	
	if len(faces) != 0:
		(Dx, Dy, frame) = computeCenter(frame, faces[0])
	else:
		Mx.reset()
		My.reset()
		
	# need to check if motion is really necessary, 
	# don't need to move if in some threshold value
	X = Mx.update(Dx)
	Y = My.update(Dy)
	print("Mx:", X, "My:", Y)
	controller.send(abs(Y), Y,-X, 100)
	#controller.send(0, 0, X, 100)
	cv2.imshow('Capture - Face detection', frame)

	#cv2.imshow("Frame", gray)
	key = cv2.waitKey(1) & 0xFF
	# if the 'q' key is pressed, stop the loop
	if key == ord("q"):
		break
	
vs.release()
cv2.destroyAllWindows()
