import cv2
from utils import toolkit
import numpy as np
from pathlib import Path 
from imutils.video import WebcamVideoStream
from rich import print as rprint
from scipy.signal import savgol_filter

def coord_tag(dict,id1,id2,size1,size2,conn2=None,filter=False):

    # Load the necessary side functions and matrix for calibration
    tool = toolkit()
    cam_mat = tool.mtx
    dist_coef = tool.dist
    y1 = 70

    # Loading the dictionnary
    marker_dict = cv2.aruco.Dictionary_get(tool.ARUCO_DICT[dict])

    # Savitzsky-Golay's filter parameters
    y_raw_value = []
    window_size = 11
    sample_size = 50
    polynomial_order = 2

    # Load the video stream
    vs = WebcamVideoStream(src=1).start()

    # Create the parameters of the camera
    param_markers = cv2.aruco.DetectorParameters_create()

    # Displayed text parameters
    fontScale = 1.5
    precision = 1

    # Program loop 
    while True:

        # Reading the frame
        frame = vs.read()

        # Adding a grey filter onto the frame
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect the tags on the image
        corners, ids, _ = cv2.aruco.detectMarkers(
            gray_frame, 
            marker_dict,
            parameters=param_markers
        )
        #bite

        try:

            # Create two separate lists for the markers with different ids and sizes
            corners1 = [corners[i] for i in range(len(ids)) if ids[i] == id1]
            corners2 = [corners[i] for i in range(len(ids)) if ids[i] == id2]
            
        
            # If the 2 tags specified have been detected then we enter the main program
            if ([id1] in ids) and ([id2] in ids):

                # Estimate the poses of the markers
                rvecs1, tvecs1, _ = cv2.aruco.estimatePoseSingleMarkers(
                    corners1,
                    size1, 
                    cam_mat,
                    dist_coef)
                rvecs2, tvecs2, _ = cv2.aruco.estimatePoseSingleMarkers(
                    corners2,
                    size2, 
                    cam_mat,
                    dist_coef)

                # Compute the homogeneous matrix 
                # Normally noglitches can happen here but be careful if there are several 
                # reference tags with the same id 
                H = tool.Homogeneous(rvecs1[0],tvecs1[0])

                # Pass tvec2 as homogenous
                tv = np.array([tvecs2[0][0][0],tvecs2[0][0][1],tvecs2[0][0][2],1])

                # Compute the tag 2 coordinates in tag 1 system of coordinates
                Tvec_id2_ref_id1 = np.dot(tv,H)
                Tvec_id2_ref_id1 = Tvec_id2_ref_id1[0:3]
                
                # Draw pose of the tags : red = Ox | green = Oy | blue = Oz 
                frame = cv2.aruco.drawDetectedMarkers(frame, corners, ids)
                frame = cv2.drawFrameAxes(frame, cam_mat, dist_coef, rvecs1, tvecs1, 0.1, 1)
                frame = cv2.drawFrameAxes(frame, cam_mat, dist_coef, rvecs2, tvecs2, 0.1, 1)

                # Extracting the bottom right coordinates of Tag 2 to plot text
                corners2 = corners2[0].reshape(4,2)
                corners2 = corners2.astype(int)
                bottom_right = corners2[2].ravel()

                # Display the newly computed coordinates of Tag 2  
                cv2.putText(
                            frame,
                            f"x:{round(Tvec_id2_ref_id1[0],precision)} y: {round(Tvec_id2_ref_id1[1],precision)} ",
                            bottom_right,
                            cv2.FONT_HERSHEY_PLAIN,
                            fontScale,
                            (255, 0, 255),
                            2,
                            cv2.LINE_AA,
                )
        # Sometimes ids is None and we get a Type error because of len(ids) but osef
        except TypeError as v:
            pass
        except Exception as e:
            rprint("[bold red] {} [/bold red]".format(e))
            pass

        # Display the frame
        cv2.imshow("Table", frame)    
        key = cv2.waitKey(1)
        
        # Close the frame is "q" is pressed
        if key == ord("q"):
            conn2.send(None)
            break

    # Finish the program cleanly
    cv2.destroyAllWindows()
    vs.stop()