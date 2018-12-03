from imutils.video import VideoStream
from imutils.video import FPS
import face_recognition
import warnings
import argparse
import datetime
import imutils
import json
import time
import cv2

def main():

        # Construct argument parser for motion detection rules
        ap = argparse.ArgumentParser()
        ap.add_argument("-c", "--conf", default="surveillance_conf.json", help="path to the JSON configuration file")
        args = vars(ap.parse_args())

        # Filter warnings and load configuration file
        warnings.filterwarnings("ignore")
        conf = json.load(open(args["conf"]))

        # Setup facial recog classifier
        face_cascade_path = "haarcascade_frontalface_default.xml"
        face_cascade = cv2.CascadeClassifier(face_cascade_path)

        # Initialize video stream and allow the camera sensor to warm up
        print("[INFO] warming up...")
        vs1 = VideoStream(src=0).start()
        vs2 = VideoStream(src=1).start()
        time.sleep(conf["camera_warmup_time"])

        # Start the FPS counter
        fps = FPS().start()

        # Store comparison frame used for motion detection
        average_frame = None

        # Loop over frames from the video file stream
        while True:

                # Set initial status message for the frame and record a timestamp
                text = "No motion detected"
                timestamp = datetime.datetime.now()

                # Grab the frame from the threaded video stream and resize it
                # to 500px (to speedup processing)
                frame = vs1.read()
                frame = imutils.resize(frame, width=500)

                # Convert the input frame from (1) BGR to grayscale (for face
                # detection)
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                # Detect faces in the grayscale frame
                faces = face_cascade.detectMultiScale(
                        gray,
                        scaleFactor=1.1,
                        minNeighbors=5,
                        minSize=(30, 30)
                )

                # Proceed if faces have been detected
                if len(faces):

                        # Draw rectangle around detected faces
                        for (x, y, w, h) in faces:
                                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 255), 2)

                # Blur the frame and initialize the average frame
                gray = cv2.GaussianBlur(gray, (21, 21), 0)
                if average_frame is None:
                        #average_frame = gray
                        average_frame = gray.copy().astype("float")
                        continue

                # Compute the absolute difference between the current frame and the previous frame
                cv2.accumulateWeighted(gray, average_frame, 0.5)
                frameDelta = cv2.absdiff(gray, cv2.convertScaleAbs(average_frame))

                # Dialate the thresholded image to fill in holes, then find contours on thresholded image
                thresh = cv2.threshold(frameDelta, conf["delta_thresh"], 255, cv2.THRESH_BINARY)[1]
                thresh = cv2.dilate(thresh, None, iterations=2)
                cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                cnts = cnts[0] if imutils.is_cv2() else cnts[1]

                # Loop over contours
                for c in cnts:

                        # If the contours is too small, ignore it
                        if cv2.contourArea(c) < conf["min_area"]:
                                continue

                        # Compute the bounding box for the contour, draw it on the frame
                        # and update the text
                        (x, y, w, h) = cv2.boundingRect(c)
                        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                        text = "Motion detected"

                # Draw the text and timestamp on the frame
                ts = timestamp.strftime("%A %d %B %Y %I:%M:%S%p")
                cv2.putText(frame, "Surveillance Status: {}".format(text), (10, 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                cv2.putText(frame, ts, (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX,
                        0.35, (0, 0, 255), 1)

                # Show the surveillance feed when should be displayed to screen
                if conf["show_video"]:
                        cv2.imshow("Surveillance Feed", frame)
                        key = cv2.waitKey(1) & 0xFF

                        # Break the loop when `q` key is pressed
                        if key == ord("q"):
                                break

        # Stop the timer and display FPS information
        fps.stop()
        print("[INFO] elapsed time: {:.2f}".format(fps.elapsed()))
        print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

        # Clean up the camera and close open windows
        vs1.stop()
        cv2.destroyAllWindows()

if __name__ == '__main__' :
	main()
