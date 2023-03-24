import numpy as np

from aruco_vision import *


font = cv2.FONT_HERSHEY_SIMPLEX

camera = RealSense()

win_name = 'Test camera vision'
cv2.namedWindow(win_name)  # , cv2.WINDOW_NORMAL
# cv2.setWindowProperty(win_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)


def debug_position_loop(cam: Camera):
    frame = cam.next_frame()
    if frame is None:
        return False
    frame = np.array(frame)
    screen_positions = {}
    for id_, corners in detect(frame):
        screen_pos = np.int32(np.mean(corners, axis=0))
        if id_ in IDS:
            screen_positions[id_] = screen_pos
            cv2.circle(frame, screen_pos, 2, (0, 0, 255), 3)
        else:
            cv2.circle(frame, screen_pos, 2, (0, 255, 0), 3)
            pos = cam.get_position(corners, 1.5)
            cv2.putText(frame, f'{pos[0]:.1f} {pos[1]:.1f}', screen_pos, font, .5, (255, 255, 255), 1, cv2.LINE_AA)

    for id_, point in cam.anchor_tag_render.items():
        cv2.circle(frame, point, 2, (255, 0, 0), 3)
        cv2.putText(frame, str(id_), point, font, .5, (192, 192, 192), 1, cv2.LINE_AA)

    if all(x in screen_positions for x in (20, 21, 22, 23)):
        if cam.old_dist is not None:
            print(f'\r{cam.old_dist = :.2f}, {cam.x = :.3f}, {cam.y = :.3f}, {cam.z = :.3f}, {cam.alpha = :.3f}, {cam.beta = :.3f}', end='')
        cam.update_physics(screen_positions)
        cam.anchor_tag_render = {id_: cam.render(point) for id_, point in real_positions.items()}
    return frame


def find_kfp_loop(cam: Camera):
    frame = cam.next_frame()
    cam.kfp = float(input('kfp ?\n'))
    if frame is None:
        return False
    frame = np.array(frame)
    cv2.circle(frame, cam.middle, 2, (0, 0, 255), 1)
    cv2.circle(frame, cam.middle * (1, 2), 2, (0, 0, 255), 1)

    screen_positions = {}
    for id_, corners in detect(frame):
        screen_pos = np.int32(np.mean(corners, axis=0))
        if id_ in IDS:
            screen_positions[id_] = screen_pos
            cv2.circle(frame, screen_pos, 2, (0, 0, 255), 3)

    cam.anchor_tag_render = {id_: cam.render(point) for id_, point in real_positions.items()}
    for id_, point in cam.anchor_tag_render.items():
        cv2.circle(frame, point, 2, (255, 0, 0), 3)
        cv2.putText(frame, str(id_), point, font, .5, (192, 192, 192), 1, cv2.LINE_AA)


    return frame

running = True
while running and cv2.getWindowProperty(win_name, cv2.WND_PROP_VISIBLE) > 0:
    frame = debug_position_loop(camera)
    if not frame is False:
        cv2.imshow(win_name, frame)
    while running and (key := cv2.pollKey()) >= 0:
        if key in (23, 27, 113):
            running = False
