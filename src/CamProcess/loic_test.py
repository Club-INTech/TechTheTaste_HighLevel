# import the opencv library
import cv2
import numpy as np
import time

dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
parameters = cv2.aruco.DetectorParameters()
detector = cv2.aruco.ArucoDetector(dictionary, parameters)

# define a video capture object
vid = cv2.VideoCapture(1)
vid.set(cv2.CAP_PROP_FRAME_WIDTH, 1600)
vid.set(cv2.CAP_PROP_FRAME_HEIGHT, 900)


while True:

    # Capture the video frame
    # by frame
    ret, frame = vid.read()
    # Display the resulting frame
    cv2.imshow('frame', frame[::-1, ::-1, :])

    print('\r', *(.25 * np.sum(corners, axis=0) for (corners,) in detector.detectMarkers(frame)[0]), sep=' ', end='')

    # the 'q' button is set as the
    # quitting button you may use any
    # desired button of your choice
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    time.sleep(1)

# After the loop release the cap object
vid.release()
# Destroy all the windows
cv2.destroyAllWindows()