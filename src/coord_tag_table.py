# import the necessary packages
from __future__ import print_function
import cv2
from utils import toolkit
import numpy as np
from pathlib import Path 
from imutils.video import WebcamVideoStream
from rich import print as rprint
from scipy.signal import savgol_filter

def coord_tag(dict,id1,id2,size,conn2=None,filter=False):

    tool = toolkit()
    marker_dict = cv2.aruco.Dictionary_get(tool.ARUCO_DICT[dict])

    cam_mat = tool.mtx
    dist_coef = tool.dist
    marker_size = size
    y1 = 70

    # Filtrering variables
    y_raw_value = []
    window_size = 11
    sample_size = 50
    polynomial_order = 2

    # creating the parameters of the camera
    vs = WebcamVideoStream(src=1).start()
    param_markers = cv2.aruco.DetectorParameters_create()

    while True : 

        frame = vs.read()
        # passing a grey filter onto the frame
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # detecting the tags
        marker_corners, marker_IDs, reject = cv2.aruco.detectMarkers(
            gray_frame, marker_dict, parameters=param_markers
        )

        if marker_corners:
            # estimating the pose of aruco markers in the image
            rVec, tVec, _ = cv2.aruco.estimatePoseSingleMarkers(
                marker_corners, marker_size, cam_mat, dist_coef
            )

            total_markers = range(0, marker_IDs.size)
            # Drawing markers onto the frame
            centers = [[],[]]
            for ids, corners, i in zip(marker_IDs, marker_corners, total_markers):

                if (ids == id1 or ids == id2):

                    cv2.polylines(
                        frame, [corners.astype(np.int32)], True, (0, 255, 255), 4, cv2.LINE_AA
                    )
                    corners = corners.reshape(4, 2)
                    (topLeft, topRight, bottomRight, bottomLeft) = corners
                    corners = corners.astype(int)
                    top_right = corners[0].ravel()
                    top_left = corners[1].ravel()
                    bottom_right = corners[2].ravel()
                    rprint("bottom right :",bottom_right)
                    bottom_left = corners[3].ravel()
                    cX = int((topLeft[0] + bottomRight[0]) / 2.0)
                    cY = int((topLeft[1] + bottomRight[1]) / 2.0)
                    cZ = 1.0 # unecessary value for the moment 
                    
                     # Computation real world coordinates using homogeneous coordinates 
                    if ids == id1:
                        centers[0] = [cX,cY]
                        # Homogeneous matrix for id1 in order to express the coordinates of the second tag in tag1's coordinate system
                        try :
                            H = tool.Homogeneous(rVec[0],tVec[0])
                        except:
                            continue
                        x1,y1 = 0,0

                    elif ids == id2 :
                        centers[1] = [cX,cY]
                        # Computing coordinates marker2 in marker1's coordinate system
                        if len(tVec) > 1:
                            try :
                                H = H
                            except: 
                                break

                            # homogeneous version of tvec
                            tv = np.array([tVec[1][0][0],tVec[1][0][1],tVec[1][0][2],1])
                            T = np.dot(tv,H)
                            if T[3] != 0:
                                T = (T)[0:3]
                            else: 
                                T = T[0:3]
                                break
                            
                            # Saving the tag's new coordinates
                            x1,y1,z1 = T[0],T[1],T[2]

                    
                    # Filtering section 
                    y_raw_value.append(y1)
                    if len(y_raw_value) > 3*sample_size:
                        window = y_raw_value[-sample_size:]
                        # Calculate the Savitzky-Golay filter
                        y_smooth = savgol_filter(window, window_size, polynomial_order)
                        y1 = y_smooth[-1]
                        rprint("[bold red]RAW value[/bold red] : {:.2f}".format(y_raw_value[-1]))
                        rprint("[bold green]FILTERED value[/bold green] : {:.2f}".format(y1))
                        
                    # Send value to the plot
                    if conn2 != None :
                        conn2.send(y1)
                    
                    # drawing the pose of the marker
                    cv2.circle(frame, (cX,cY), 4, (0, 0, 255), -1)
                    # drawing pose OX is drawn in red, OY in green and OZ in blue.
                    point = cv2.drawFrameAxes(frame, cam_mat, dist_coef, rVec[i], tVec[i], 0.25, 3)
                    
                    if ids == id1:
                        cv2.putText(
                            frame,
                            f"x:{tVec[i][0][1]} y: {0} ",
                            bottom_right,
                            cv2.FONT_HERSHEY_PLAIN,
                            2.0,
                            (255, 0, 255),
                            2,
                            cv2.LINE_AA,
                        )
                    elif ids == id2:
                        try :
                            cv2.putText(
                                frame,
                                f"x:{round(x1,1)} y: {round(y1,1)} ",
                                bottom_right,
                                cv2.FONT_HERSHEY_PLAIN,
                                2.0,
                                (255, 0, 255),
                                2,
                                cv2.LINE_AA,
                            )
                        except: 
                            pass
                    
                if centers[0] != [] and centers[1] != []:
                    cv2.line(frame, centers[0], centers[1], (255, 0, 0), 2)

        cv2.imshow("Table", frame)    
        key = cv2.waitKey(60)

        if key == ord("q"):
            conn2.send(None)
            break

    cv2.destroyAllWindows()
    vs.stop()