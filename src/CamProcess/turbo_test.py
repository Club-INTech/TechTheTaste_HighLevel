import cv2
import time

win_name = 'Test camera vision'
cv2.namedWindow(win_name, cv2.WINDOW_NORMAL)
cv2.setWindowProperty(win_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
vid = cv2.VideoCapture(1, cv2.CAP_DSHOW)
vid.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
vid.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

with open('giga_test.py', 'r') as f:
    exec(f.read())
_, frame = vid.read()
DETECT = Detector(frame)


while cv2.getWindowProperty(win_name, cv2.WND_PROP_VISIBLE) > 0:
    ret, frame = vid.read()
    date = time.perf_counter()
    DETECT(frame)
    print(' frame time', time.perf_counter() - date, end='')
    cv2.imshow(win_name, frame)
    if cv2.waitKey(1) & 0xff == ord(' '):
        _Detector = Detector
        try:
            with open('giga_test.py', 'r') as f:
                exec(f.read())
            DETECT = Detector(frame)
        except Exception as e:
            print(e)
            Detector = _Detector
            DETECT = Detector(frame)
vid.release()
cv2.destroyAllWindows()
