import numpy as np

from aruco_vision import *


font = cv2.FONT_HERSHEY_SIMPLEX


win_name = 'Test camera vision'
cv2.namedWindow(win_name, cv2.WINDOW_NORMAL)  #
cv2.setWindowProperty(win_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)


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
        print(f'\r{cam.x = :.3f}, {cam.y = :.3f}, {cam.z = :.3f}, {cam.alpha = :.3f}, {cam.beta = :.3f}', end='')
        cam.find_physics_cross_ratio(screen_positions)
        cam.anchor_tag_render = {id_: cam.render(point) for id_, point in real_positions.items()}
    return frame


def test_manual_detection(cam: Camera):
    frame = cam.next_frame()
    if frame is None:
        return False
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # frame = np.uint8(255 * (frame > 150))
    frame = cv2.adaptiveThreshold(frame, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 23, 12)
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


colors = (255, 0, 0), (0, 255, 0), (0, 0, 255), (128, 128, 255)


def new_loop(cam: Camera):
    frame = np.array(cam.next_frame())
    screen_positions = {}
    for id_, corners in detect(frame):
        for i in range(4):
            cv2.line(frame, corners[i - 1], corners[i], colors[i], 3)
        point = line_intersection(corners[0], corners[2], corners[1], corners[3])
        cv2.circle(frame, np.int32(point), 2, (255, 0, 0), 3)
        if id_ in real_positions:
            screen_positions[id_] = point

    cv2.circle(frame, cam.middle, 2, (255, 0, 0), 3)
    if len(screen_positions) == 4:
        cam.find_physics_cross_ratio(screen_positions)
        print(f'\r{cam.alpha = :.3f} {cam.beta = :.3f} {cam.kfp = :.3f} {cam.optic_center =}', end='')
        for id_ in IDS:
            cv2.circle(frame, cam.render(real_positions[id_]), 2, (0, 255, 0), 3)

    return frame


def camera_test():
    camera = LogitechCamera(0)

    running = True
    while running and cv2.getWindowProperty(win_name, cv2.WND_PROP_VISIBLE) > 0:
        frame = debug_position_loop(camera)
        cv2.imshow(win_name, frame)
        while running and (key := cv2.pollKey()) >= 0:
            if key in (23, 27, 113):
                running = False


def draw_detected(frame):
    for id_, corners in detect(frame):
        for i in range(4):
            cv2.line(frame, corners[i - 1], corners[i], colors[i], 4)
        point = line_intersection(corners[0], corners[2], corners[1], corners[3])
        cv2.circle(frame, np.int32(point), 3, (0, 0, 255), 4)


def photo_test():
    running = True
    import os
    path = 'PHOTOS'
    imgs = [cv2.imread(os.path.join(path, im)) for im in os .listdir(path)]
    for im in imgs:
        draw_detected(im)
    index = 0
    frame = imgs[index]
    while running and cv2.getWindowProperty(win_name, cv2.WND_PROP_VISIBLE) > 0:
        cv2.imshow(win_name, frame)
        while running and (key := cv2.pollKey()) >= 0:
            if key in (23, 27, 113):
                running = False
            if key == 2424832:
                index = (index - 1) % len(imgs)
                frame = imgs[index]
            if key == 2555904:
                index = (index + 1) % len(imgs)
                frame = imgs[index]
            else:
                print(key)

camera_test()
