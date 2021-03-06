from __future__ import print_function
from motionfacialdetection import MotionFacialDetection
from emailnotification import EmailNotification
from imutils.video import VideoStream
import numpy as np
import datetime
import warnings
import argparse
import imutils
import json
import time
import cv2

# Construct argument parser for detection configuration
ap = argparse.ArgumentParser()
ap.add_argument("-c", "--conf", default="rpysurveillance.json", help="path to the JSON configuration file")
args = vars(ap.parse_args())

# Filter warnings and load configuration file
warnings.filterwarnings("ignore")
conf = json.load(open(args["conf"]))

# Initialize gmail notification
print("[INFO] configuring email notifications...")
emailNotification = EmailNotification(
    conf["email_server"],
    conf["email_port"],
    conf["email_sender"],
    conf["email_password"],
    conf["email_recipients"]
)

# Initialize the video streams and allow them to warmup
print("[INFO] starting cameras...")
cam1 = VideoStream(src=0).start()
cam2 = VideoStream(src=1).start()
time.sleep(conf["camera_warmup_time"])

# Initialize the two motion/facial detectors
cam1Detect = MotionFacialDetection(
    conf["accum_weight"],
    conf["delta_thresh"],
    conf["min_area"],
    conf["scale_factor"],
    conf["min_neighbors"],
    tuple(conf["min_size"].split(","))
)
cam2Detect = MotionFacialDetection(
    conf["accum_weight"],
    conf["delta_thresh"],
    conf["min_area"],
    conf["scale_factor"],
    conf["min_neighbors"],
    tuple(conf["min_size"].split(","))
)

# Initialize total number of frames counter
total = 0

# Initialize email sending flags that sets email notification intervals in seconds
sendingMotionTime = time.time()
sendingFacialTime = time.time()

# Loop over the frames from the video streams
while True:

    # Initialize the list of frames that have been processed
    procFrames = []

    # Loop over the frames and their detectors
    for (stream, detect) in zip((cam1, cam2), (cam1Detect, cam2Detect)):

        # Read the next frame from the video stream and resize it to
        # have a maximum width of 400 pixels and convert frame to grayscale
        frame = stream.read()
        frame = imutils.resize(frame, width=500)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Update/run the facial detector
        if conf["facial_detect"]:
            faceLocs = detect.updateFacial(gray)

        # Update/run the motion detector locations
        motionLocs = detect.updateMotion(gray)

        # Allow the detector to run for enough frames to compute an average
        if total < 32:
            procFrames.append(frame)
            continue

        # Check for facial detection when configuration set to do so
        if conf["facial_detect"]:

            # Proceed when facial coordinates detected
            if len(faceLocs) > 0:

                # Draw rectangle around detected faces
                for (x, y, w, h) in faceLocs:
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 255), 2)

                # Send email when face detected at no greater than set interval in seconds
                currentFacialTime = time.time()
                if (currentFacialTime - sendingFacialTime > conf["email_facial_notification_interval"]) & (conf["facial_notification_on"] == True):

                    # Send and notify of the gmail notification sent
                    print(conf["email_facial_message"])
                    faceMessage = conf["email_facial_message"]
                    emailNotification.send(faceMessage, frame, "face-")

                    # Reset sending flag
                    sendingFacialTime = currentFacialTime

        # Check for motion detection
        if len(motionLocs) > 0:

            # Initialize the minimum and maximum (x, y) coordinates
            (minX, minY) = (np.inf, np.inf)
            (maxX, maxY) = (-np.inf, -np.inf)

            # Loop over the locations of motion and accumulate the minimum
            # and maximum locations of the bounding boxes
            for l in motionLocs:
                (x, y, w, h) = cv2.boundingRect(l)
                (minX, maxX) = (min(minX, x), max(maxX, x + w))
                (minY, maxY) = (min(minY, y), max(maxY, y + h))

            # Draw the bounding box
            cv2.rectangle(frame, (minX, minY), (maxX, maxY), (0, 0, 255), 2)

            # Send email when face detected at no greater than set interval in seconds
            currentMotionTime = time.time()
            if (currentMotionTime - sendingMotionTime > conf["email_motion_notification_interval"]) & (conf["motion_notification_on"] == True):

                # Send and notify of the gmail notification sent
                print(conf["email_motion_message"])
                motionMessage = conf["email_motion_message"]
                emailNotification.send(motionMessage, frame, "motion-")

                # Reset sending flag
                sendingMotionTime = currentMotionTime

        # Update the processed frames list
        procFrames.append(frame)

    # Increment the total number of frames
    total += 1

    # Loop over the frames a second time
    if conf["show_video"]:
        timestamp = datetime.datetime.now()
        ts = timestamp.strftime("%A %d %B %Y %I:%M:%S%p")
        for (frame, name) in zip(procFrames, ("Cam 1", "Cam 2")):

            # Draw the timestamp on the frame and display it
            cv2.putText(frame, ts, (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)
            cv2.imshow(name, frame)

            # Encode the frame as JPEG
            jpeg = cv2.imencode('.jpg', frame)

    # Check to see if a key was pressed
    key = cv2.waitKey(1) & 0xFF

    # If the `q` key was pressed break from the loop
    if key == ord("q"):
        break

# Cleanup and stop the cameras
print("[INFO] cleaning up...")
cv2.destroyAllWindows()
cam1.stop()
cam2.stop()
