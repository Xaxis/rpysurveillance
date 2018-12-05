import imutils
import cv2

class MotionFacialDetection:

    def __init__(
            self,
            accumWeight,
            deltaThresh,
            minArea,
            scaleFactor,
            minNeighbors,
            minSize):

        # Set the OpenCV version and motion detection configuration
        self.isv2 = imutils.is_cv2()
        self.accumWeight = accumWeight
        self.deltaThresh = deltaThresh
        self.minArea = minArea

        # Setup facial recog configuration
        self.scaleFactor = scaleFactor
        self.minNeighbors = minNeighbors
        self.minSize = (int(minSize[0]), int(minSize[1]))

        # Setup facial recog classifier
        self.faceCascadePath = "haarcascade_frontalface_default.xml"
        self.faceCascade = cv2.CascadeClassifier(self.faceCascadePath)

        # Initialize the average image for motion detection
        self.averageFrame = None

    def updateMotion(self, frame):

        # Initialize the list of motion locations
        motionLocs = []

        # Add gaussian blur to frame
        frame = cv2.GaussianBlur(frame, (21, 21), 0)

        # Initialize the average frame
        if self.averageFrame is None:
            self.averageFrame = frame.copy().astype("float")
            return motionLocs

        # Compute the absolute difference between the current frame and the previous frame
        cv2.accumulateWeighted(frame, self.averageFrame, self.accumWeight)
        frameDelta = cv2.absdiff(frame, cv2.convertScaleAbs(self.averageFrame))

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

        # Initialize detected face locations
        faceLocs = self.faceCascade.detectMultiScale(
            frame,
            scaleFactor=self.scaleFactor,
            minNeighbors=self.minNeighbors,
            minSize=self.minSize
        )

        # Return detected faces
        return faceLocs
