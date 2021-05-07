from imutils.video import VideoStream
import imutils
import time
import cv2
from collections import deque 
import numpy as np

face_cascade = cv2.CascadeClassifier()
face_cascade.load(cv2.samples.findFile('/home/nteplitskiy/Documents/Classes/Final_Project/slab/venv/lib64/python3.9/site-packages/cv2/data/haarcascade_frontalface_alt.xml'))
# lol

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
	cv2.arrowedLine(frame, face_center, frame_center, (0,255,0),3,8,0,0.1)
	return frame

while True:
	frame = vs.read()
	if frame is None:
		break;
	
	frame = imutils.resize(frame, width=600)
	frame, faces = detectAndDisplay(frame)
	
	frame_center = frame.shape[1]//2, frame.shape[0]//2
	cv2.circle(frame,frame_center,4,(0,0,255),6)
	
	if len(faces) != 0:
		frame = computeCenter(frame, faces[0])
		
	cv2.imshow('Capture - Face detection', frame)

	#cv2.imshow("Frame", gray)
	key = cv2.waitKey(1) & 0xFF
	# if the 'q' key is pressed, stop the loop
	if key == ord("q"):
		break
	
vs.release()
cv2.destroyAllWindows()
