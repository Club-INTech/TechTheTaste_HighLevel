# this script implements the standard functions we will use in this project
import cv2
import numpy as np
from pathlib import Path 
import glob
from math import sin, cos
import datetime
from threading import Thread
import timeit
from scipy.signal import savgol_filter

class toolkit : 

    def __init__(self):
        # ——————————————— Parameters of the logitech camera ———————————————
        path = Path.cwd()
        calib_data_path = path / 'MultiMatrix.npz'
        data = np.load(calib_data_path)
        self.mtx = data["camMatrix"]
        self.dist = data["distCoef"]
        self.rvec_cam = data["rVector"]
        self.tvec_cam = data["tVector"]

        # Define the window size and polynomial order
        self.window_size = 5
        self.polynomial_order = 2
    
        # declaring the homogeneous matrix
        theta = 52
        tx,ty,tz = -100,168,0
        self.H = np.array([[1,0,0,tx],
            [0,cos(theta), -sin(theta),ty],
            [0,sin(theta),cos(theta),tz],
            [0,0,0,1]])

        self.ARUCO_DICT = {
                        "DICT_4X4_50": cv2.aruco.DICT_4X4_50,
                        "DICT_4X4_100": cv2.aruco.DICT_4X4_100,
                        "DICT_4X4_250": cv2.aruco.DICT_4X4_250,
                        "DICT_4X4_1000": cv2.aruco.DICT_4X4_1000,
                        "DICT_5X5_50": cv2.aruco.DICT_5X5_50,
                        "DICT_5X5_100": cv2.aruco.DICT_5X5_100,
                        "DICT_5X5_250": cv2.aruco.DICT_5X5_250,
                        "DICT_5X5_1000": cv2.aruco.DICT_5X5_1000,
                        "DICT_6X6_50": cv2.aruco.DICT_6X6_50,
                        "DICT_6X6_100": cv2.aruco.DICT_6X6_100,
                        "DICT_6X6_250": cv2.aruco.DICT_6X6_250,
                        "DICT_6X6_1000": cv2.aruco.DICT_6X6_1000,
                        "DICT_7X7_50": cv2.aruco.DICT_7X7_50,
                        "DICT_7X7_100": cv2.aruco.DICT_7X7_100,
                        "DICT_7X7_250": cv2.aruco.DICT_7X7_250,
                        "DICT_7X7_1000": cv2.aruco.DICT_7X7_1000,
                        "DICT_ARUCO_ORIGINAL": cv2.aruco.DICT_ARUCO_ORIGINAL,
                        "DICT_APRILTAG_16h5": cv2.aruco.DICT_APRILTAG_16h5,
                        "DICT_APRILTAG_25h9": cv2.aruco.DICT_APRILTAG_25h9,
                        "DICT_APRILTAG_36h10": cv2.aruco.DICT_APRILTAG_36h10,
                        "DICT_APRILTAG_36h11": cv2.aruco.DICT_APRILTAG_36h11
                    }

        
    def DrawTag(self,corners, ids, rejected,frame,detectID=None,markersizeCM=None):
        """
        Draw the box around the ArUco tags if they are detected.
        If dist is fullfilled with an int, the function only draws a box 
        around the marker of ID == dist
        """
        if len(corners) > 0:
            # flatten the ArUco IDs list
            ids = ids.flatten()
            # loop over the detected ArUCo corners
            for (markerCorner, markerID) in zip(corners, ids):
                if detectID == None:
                    # extract the marker corners (which are always returned
                    # in top-left, top-right, bottom-right, and bottom-left
                    # order)
                    corners = markerCorner.reshape((4, 2))
                    (topLeft, topRight, bottomRight, bottomLeft) = corners
                    # convert each of the (x, y)-coordinate pairs to integers
                    topRight = (int(topRight[0]), int(topRight[1]))
                    bottomRight = (int(bottomRight[0]), int(bottomRight[1]))
                    bottomLeft = (int(bottomLeft[0]), int(bottomLeft[1]))
                    topLeft = (int(topLeft[0]), int(topLeft[1]))
                    # draw the bounding box of the ArUCo detection
                    cv2.line(frame, topLeft, topRight, (0, 255, 0), 2)
                    cv2.line(frame, topRight, bottomRight, (0, 255, 0), 2)
                    cv2.line(frame, bottomRight, bottomLeft, (0, 255, 0), 2)
                    cv2.line(frame, bottomLeft, topLeft, (0, 255, 0), 2)
                    # compute and draw the center (x, y)-coordinates of the
                    # ArUco marker
                    cX = int((topLeft[0] + bottomRight[0]) / 2.0)
                    cY = int((topLeft[1] + bottomRight[1]) / 2.0)
                    cv2.circle(frame, (cX, cY), 4, (0, 0, 255), -1)
                    # draw the ArUco marker ID on the frame
                    cv2.putText(frame, str(markerID),
                        (topLeft[0], topLeft[1] - 15),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5, (0, 255, 0), 2)
                elif markerID == detectID:
                    # extract the marker corners (which are always returned
                    # in top-left, top-right, bottom-right, and bottom-left
                    # order)
                    corners = markerCorner.reshape((4, 2))
                    (topLeft, topRight, bottomRight, bottomLeft) = corners
                    # convert each of the (x, y)-coordinate pairs to integers
                    topRight = (int(topRight[0]), int(topRight[1]))
                    bottomRight = (int(bottomRight[0]), int(bottomRight[1]))
                    bottomLeft = (int(bottomLeft[0]), int(bottomLeft[1]))
                    topLeft = (int(topLeft[0]), int(topLeft[1]))
                    # draw the bounding box of the ArUCo detection
                    cv2.line(frame, topLeft, topRight, (0, 255, 0), 2)
                    cv2.line(frame, topRight, bottomRight, (0, 255, 0), 2)
                    cv2.line(frame, bottomRight, bottomLeft, (0, 255, 0), 2)
                    cv2.line(frame, bottomLeft, topLeft, (0, 255, 0), 2)
                    # compute and draw the center (x, y)-coordinates of the
                    # ArUco marker
                    cX = int((topLeft[0] + bottomRight[0]) / 2.0)
                    cY = int((topLeft[1] + bottomRight[1]) / 2.0)
                    rvec , tvec, _ = cv2.aruco.estimatePoseSingleMarkers(corners, markersizeCM, self.mtx, self.dist)
                    cv2.circle(frame, (cX, cY), 4, (0, 0, 255), -1)
                    # draw the ArUco marker ID on the frame
                    """cv2.putText(frame, str(tvec[2]),
                        (topLeft[0], topLeft[1] - 15),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5, (0, 255, 0), 2)"""    

    def Homogeneous(self,r_,t_):
        """
        Creates the 4x4 homogeneous matrix associated to the roation and translation vector rvec and tvec 
        """
        # first let's compute the rotation matrix associated to the rotation vector r_
        R = cv2.Rodrigues(r_)[0]
        H = np.array([
            [R[0][0],R[0][1],R[0][2],t_[0][0]],
            [R[1][0],R[1][1],R[1][2],t_[0][1]],
            [R[2][0],R[2][1],R[2][2],t_[0][2]],
            [0,0,0,1]
                ])
        return H
    
    def filter_bary(val_n,coef,val_p=None):
        """
        0 < coef < 1
        Returns coef*val_p + (1-coef)*val_n
        """
        if val_p==None : 
            return val_n
        else : 
            return coef*val_p + (1-coef)*val_n

class FPS:

	def __init__(self):
		# store the start time, end time, and total number of frames
		# that were examined between the start and end intervals
		self._start = None
		self._end = None
		self._numFrames = 0

	def start(self):
		# start the timer
		self._start = datetime.datetime.now()
		return self

	def stop(self):
		# stop the timer
		self._end = datetime.datetime.now()
    
	def update(self):
		# increment the total number of frames examined during the
		# start and end intervals
		self._numFrames += 1

	def elapsed(self):
		# return the total number of seconds between the start and
		# end interval
		return (self._end - self._start).total_seconds()

	def fps(self):
		# compute the (approximate) frames per second
		return self._numFrames / self.elapsed()
class WebcamVideoStream:
	def __init__(self, src=0):
		# initialize the video camera stream and read the first frame
		# from the stream
		self.stream = cv2.VideoCapture(src)
		(self.grabbed, self.frame) = self.stream.read()
		# initialize the variable used to indicate if the thread should
		# be stopped
		self.stopped = False

	def start(self):
		# start the thread to read frames from the video stream
		Thread(target=self.update, args=()).start()
		return self

	def update(self):
		# keep looping infinitely until the thread is stopped
		while True:
			# if the thread indicator variable is set, stop the thread
			if self.stopped:
				return
			# otherwise, read the next frame from the stream
			(self.grabbed, self.frame) = self.stream.read()

	def read(self):
		# return the frame most recently read
		return self.frame
        
	def stop(self):
		# indicate that the thread should be stopped
		self.stopped = True

if "__name__" == "__main__": 
    tool = toolkit()