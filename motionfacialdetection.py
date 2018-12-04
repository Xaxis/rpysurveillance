import imutils
import cv2

class MotionFacialDetection:

    def __init__(self, accumWeight=0.5, deltaThresh=5, minArea=5000):

        # Set the OpenCV version and detection configuration
        self.isv2 = imutils.is_cv2()
        self.accumWeight = accumWeight
        self.deltaThresh = deltaThresh
        self.minArea = minArea

        # Setup facial recog classifier
        self.faceCascadePath = "haarcascade_frontalface_default.xml"
        self.faceCascade = cv2.CascadeClassifier(self.faceCascadePath)

        # Initialize the average image for motion detection
        self.averageFrame = None

    def updateMotion(self, frame):

        # Initialize the list of motion locations
        motionLocs = []

        # Convert the input frame from BGR to grayscale and gaussian blur
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)

        # Initialize the average frame
        if self.averageFrame is None:
            self.averageFrame = gray.copy().astype("float")
            return motionLocs

        # Compute the absolute difference between the current frame and the previous frame
        cv2.accumulateWeighted(gray, self.averageFrame, self.accumWeight)
        frameDelta = cv2.absdiff(gray, cv2.convertScaleAbs(self.averageFrame))

        # Threshold the delta frame and apply a series of dilations to help fill in holes
        thresh = cv2.threshold(frameDelta, self.deltaThresh, 255, cv2.THRESH_BINARY)[1]
        thresh = cv2.dilate(thresh, None, iterations=2)

        # Find contours in the thresholded image, taking care to use the appropriate version
        # of OpenCV
        cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = cnts[0] if self.isv2 else cnts[1]

        # Loop over the contours
        for c in cnts:

            # Only add the contour to the motion locations list if it exceeds the minimum area
            if cv2.contourArea(c) > self.minArea:
                motionLocs.append(c)

        # Return the set of locations
        return motionLocs

    def updateFacial(self, frame):

        # Convert the input frame from BGR to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Initialize detected face locations
        faceLocs = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )

        # Return detected faces
        return faceLocs
