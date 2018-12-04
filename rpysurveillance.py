from __future__ import print_function
from motionfacialdetection import MotionFacialDetection
from imutils.video import VideoStream
import numpy as np
import datetime
import imutils
import time
import cv2

# Initialize the video streams and allow them to warmup
print("[INFO] starting cameras...")
cam1 = VideoStream(src=0).start()
cam2 = VideoStream(src=1).start()
time.sleep(2.0)

# Initialize the two motion/facial detectors, along with the total number of frames read
cam1Detect = MotionFacialDetection()
cam2Detect = MotionFacialDetection()
total = 0

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
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Update/run the facial detector
        faceLocs = detect.updateFacial(frame)

        # Update/run the motion detector locations
        motionLocs = detect.updateMotion(frame)

        # Allow the detector to run for enough frames to compute an average
        if total < 32:
            procFrames.append(frame)
            continue

        # Check for facial detection
        if len(faceLocs) > 0:

            # Draw rectangle around detected faces
            for (x, y, w, h) in faceLocs:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 255), 3)

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
            cv2.rectangle(frame, (minX, minY), (maxX, maxY), (0, 0, 255), 3)

        # Update the processed frames list
        procFrames.append(frame)

    # Increment the total number of frames read and grab the current timestamp
    total += 1
    timestamp = datetime.datetime.now()
    ts = timestamp.strftime("%A %d %B %Y %I:%M:%S%p")

    # Loop over the frames a second time
    for (frame, name) in zip(procFrames, ("Cam 1", "Cam 2")):

        # Draw the timestamp on the frame and display it
        cv2.putText(frame, ts, (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)
        cv2.imshow(name, frame)

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
