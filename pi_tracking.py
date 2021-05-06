# USAGE
# python multi_object_tracking.py --video videos/soccer_01.mp4 --tracker csrt
#using the videos

#python multi_object_tracking.py  --tracker csrt
#using vid from cam
#if cam isnt detected then it wont work

#press s to stop the video and then highlight using the mouse and press spacebar to continue

# import the necessary packages
from imutils.video import VideoStream
import argparse
import imutils
import time
import cv2

import serial 
import sys
import struct 

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", type=str,
	help="path to input video file")
ap.add_argument("-t", "--tracker", type=str, default="kcf",
	help="OpenCV object tracker type")
ap.add_argument("-s", "--serial", type=str,
        help="Path to arduino motor controller")
ap.add_argument("-pi", action='store_true')
args = vars(ap.parse_args())

# initialize a dictionary that maps strings to their corresponding
# OpenCV object tracker implementations
OPENCV_OBJECT_TRACKERS = {
	"csrt": cv2.TrackerCSRT_create,
	"kcf": cv2.TrackerKCF_create,
	"boosting": cv2.TrackerBoosting_create,
	"mil": cv2.TrackerMIL_create,
	"tld": cv2.TrackerTLD_create,
	"medianflow": cv2.TrackerMedianFlow_create,
	"mosse": cv2.TrackerMOSSE_create
}

# initialize OpenCV's special multi-object tracker
trackers = cv2.MultiTracker_create()


ser = serial.Serial(args["serial"], 115200, timeout=1)


# if a video path was not supplied, grab the reference to the web cam
if not args.get("video", False):
	print("[INFO] starting video stream...")
	vs = VideoStream(src=0).start()
	time.sleep(1.0)

# otherwise, grab a reference to the video file
else:
	vs = cv2.VideoCapture(args["video"])

def send_data(s_speed, s_step, d_speed, d_step):
	commands = struct.pack('<i', s_speed) + struct.pack('<h', s_step) + struct.pack('<h', d_speed) + struct.pack('<h', d_step)
	checksum = sum(commands)
	ser.write(commands + struct.pack('<h', checksum))

def compute_vector(x,y,w,h):
    return x+w//2, y+h//2

# loop over frames from the video stream
while True:
	# grab the current frame, then handle if we are using a
	# VideoStream or VideoCapture object
	frame = vs.read()
	frame = frame[1] if args.get("video", False) else frame

	# check to see if we have reached the end of the stream
	if frame is None:
		break

	# resize the frame (so we can process it faster)
	if args.get('pi'):
		frame = imutils.resize(frame, width=200)
	else:
		frame = imutils.resize(frame, width=600)
	#print(frame.shape)
	center = frame.shape[1]//2, frame.shape[0]//2
	cv2.circle(frame,center,4,(0,0,255),6)
	# grab the updated bounding box coordinates (if any) for each
	# object that is being tracked
	(success, boxes) = trackers.update(frame)

	# loop over the bounding boxes and draw then on the frame
	for box in boxes:
		(x, y, w, h) = [int(v) for v in box]
		cp = compute_vector(x,y,w,h)
		cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
		cv2.arrowedLine(frame, cp, center, (0,255,0),3,8,0,0.1)
		if x > center[0]:
			print(x-center[0])
			send_data(0,0,-100,100)
		if x + w < center[0]:
			print(x + w - center[0])
			send_data(0,0,100,100)
		
	# show the output frame
	cv2.imshow("Frame", frame)
	key = cv2.waitKey(1) & 0xFF

	# if the 's' key is selected, we are going to "select" a bounding
	# box to track
	if key == ord("s"):
		# select the bounding box of the object we want to track (make
		# sure you press ENTER or SPACE after selecting the ROI)
		box = cv2.selectROI("Frame", frame, fromCenter=False,
			showCrosshair=True)

		# create a new object tracker for the bounding box and add it
		# to our multi-object tracker
		tracker = OPENCV_OBJECT_TRACKERS[args["tracker"]]()
		trackers.add(tracker, frame, box)

	# if the `q` key was pressed, break from the loop
	elif key == ord("q"):
		break

# if we are using a webcam, release the pointer
if not args.get("video", False):
	vs.stop()

# otherwise, release the file pointer
else:
	vs.release()

# close all windows
cv2.destroyAllWindows()
ser.close()
