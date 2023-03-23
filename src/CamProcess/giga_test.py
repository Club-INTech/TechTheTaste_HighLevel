import numpy as np
import cv2
import scipy
from frechetdist import frdist


print('\nUpdating')

font = cv2.FONT_HERSHEY_SIMPLEX


BETA = 1.5  # 0.745
ALPHA = .15  # 0.0598

OX = 40  # 33.
OY = -20  # -58.
OZ = 110  # 96
CAMERA = np.array([OX, OY, OZ])

KFP = 960. * (1920 / 1600)

positions = {
    21: np.array([0., 0., 0.]),
    20: np.array([86., 0., 0.]),
    23: np.array([0., 185., 0.]),
    22: np.array([86., 185., 0.])
}

COS_A, SIN_A, COS_B, SIN_B, VEC, XP, YP = 0, 0, 0, 0, 0, 0, 0


def compute_variables():
    global COS_A, SIN_A, COS_B, SIN_B, VEC, XP, YP, CAMERA
    COS_A, SIN_A, COS_B, SIN_B = np.cos(ALPHA), np.sin(ALPHA), np.cos(BETA), np.sin(BETA)
    VEC = np.array([SIN_A * COS_B, COS_A * COS_B, - SIN_B])
    XP = np.array([COS_A, -SIN_A, 0.])
    YP = np.cross(XP, VEC)
    CAMERA = np.array([OX, OY, OZ])


compute_variables()


def render(middle):
    for id_, point in positions.items():
        v = point - CAMERA
        v *= KFP / np.dot(v, VEC)
        yield id_, np.array([np.dot(XP, v) + middle[0], -np.dot(YP, v) + middle[1]], np.int32)


def render_point(middle, point):
    v = point - CAMERA
    v *= KFP / np.dot(v, VEC)
    return np.array([np.dot(XP, v) + middle[0], -np.dot(YP, v) + middle[1]], np.int32)


def _jacobian(middle):
    def jacobian(pos):
        # test = render_point(middle, np.append(pos, (.0,)))
        vec = np.append(pos, [0])
        v = vec - CAMERA
        dotv, dotx, doty = np.dot(v, VEC), np.dot(v, XP), np.dot(v, YP)
        j = np.zeros((2, 2), float)

        j[0, 0] = (COS_A * dotv - SIN_A * COS_B * dotx)  # * test[0]
        j[0, 1] = (-SIN_A * dotv - COS_A * COS_B * dotx)  # * test[0]
        j[1, 0] = -(SIN_A * SIN_B * dotv - SIN_A * COS_B * doty)  # * test[1]
        j[1, 1] = -(COS_A * SIN_B * dotv - COS_A * COS_B * doty)  # * test[1]

        return j * KFP / dotv ** 2
    return jacobian


def find_pos(middle, point):
    def f(pos):
        return render_point(middle, np.append(pos, (.0,))) - point

    return scipy.optimize.fsolve(f, np.array([50, 50]), fprime=_jacobian(middle))


def find_physics(screen_positions, middle):
    global ALPHA, BETA, OX, OY, OZ

    def frechet(values):
        alpha, beta, Ox, Oy, Oz = values
        kfp = KFP
        cos_a, sin_a = np.cos(alpha), np.sin(alpha)
        cos_b, sin_b = np.cos(beta), np.sin(beta)
        v, xp = np.array([sin_a * cos_b, cos_a * cos_b, -sin_b]), np.array([cos_a, -sin_a, 0])
        yp = np.cross(xp, v)
        camera = np.array([Ox, Oy, Oz])

        curve = []
        for id_ in (20, 21, 23, 22):
            real = positions[id_]
            ox = real - camera
            ox *= kfp / np.dot(ox, v)
            curve.append(np.array([np.dot(xp, ox) + middle[0], -np.dot(yp, ox) + middle[1]], np.int32))
        return frdist(curve, tuple(screen_positions[id_] for id_ in (20, 21, 23, 22)))

    ALPHA, BETA, OX, OY, OZ = scipy.optimize.minimize(
        frechet, np.array([ALPHA, BETA, OX, OY, OZ], float),
        method='Powell',
        bounds=((-np.pi / 4, np.pi / 4), (0., np.pi/2), (0., 100.), (-90., -10.), (70., 130.))
    ).x
    compute_variables()


# def find_physics(screen_positions):
#     def try_render(value):
#         Ox, Oy, Oz, alpha, beta, kfp = value
#         cos_a, sin_a = np.cos(alpha), np.sin(alpha)
#         cos_b, sin_b = np.cos(beta), np.sin(beta)
#         v, xp = np.array([sin_a * cos_b, cos_a * cos_b, -sin_b]), np.array([cos_a, -sin_a, 0])
#         yp = np.cross(xp, v)
#         camera = np.array([Ox, Oy, Oz])
#
#         res = np.array([], float)
#         for id_ in positions:
#             real = positions[id_]
#             OX = real - camera
#             OX *= kfp / np.dot(OX, v)
#             res = np.append(res, ((np.array([np.dot(OX, xp), np.dot(OX, yp)]) - screen_positions[id_]),))
#         return res
#
#     def jacobian(value):
#         Ox, Oy, Oz, alpha, beta, kfp = value
#         cos_a, sin_a = np.cos(alpha), np.sin(alpha)
#         cos_b, sin_b = np.cos(beta), np.sin(beta)
#         v, xp = np.array([sin_a * cos_b, cos_a * cos_b, -sin_b]), np.array([cos_a, -sin_a, 0])
#         yp = np.cross(xp, v)
#         camera = np.array([Ox, Oy, Oz])
#
#         j = np.zeros((6, 6), float)
#
#         for i, id_ in enumerate(positions):
#             real = positions[id_]
#             OX = real - camera
#             dotv, doty, dotx = np.dot(OX, v), np.dot(OX, yp), np.dot(OX, xp)
#
#             # d/dOx
#             j[0, 2 * i] = kfp * (-cos_b * sin_a * dotx + cos_a * dotv) / dotv ** 2
#             j[0, 2 * i + 1] = kfp * (-sin_b * sin_a * doty + sin_b * sin_a * dotv) / dotv ** 2
#
#             # d/dOy
#             j[1, 2 * i] = kfp * (-cos_b * cos_a * dotx + sin_a * dotv) / dotv ** 2
#             j[1, 2 * i + 1] = kfp * (-cos_b * cos_a * doty + sin_b * cos_a * dotv) / dotv ** 2
#
#             # d/dOz
#             j[2, 2 * i] = kfp * dotx * (-cos_b) / dotv ** 2
#             j[2, 2 * i + 1] = kfp * (sin_b * dotv - cos_b * doty) / dotv ** 2
#
#
#             # d/dalpha
#             j[3, 2 * i] = kfp * (np.dot(OX, (-sin_a, -cos_a, 0)) * dotv - cos_b * dotx ** 2) / dotv ** 2
#             j[3, 2 * i + 1] = kfp * (sin_b * dotx * dotv - cos_b * dotx * doty) / dotv ** 2
#
#             # d/dbeta
#             j[4, 2 * i] = kfp * dotx * doty / dotv ** 2
#             j[4, 2 * i + 1] = kfp * (1 + (doty / dotv) ** 2)
#
#             # d/dkfp
#             j[5, 2 * i] = dotx / dotv
#             j[5, 2 * i + 1] = doty / dotv
#         return j
#
#     print('\r', *scipy.optimize.fsolve(try_render, np.array([50., -60., 100., 0., np.pi / 8,  1.]), fprime=jacobian), end='')



class Detector:
    def __init__(self, frame):
        dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
        parameters = cv2.aruco.DetectorParameters()
        self.detector = cv2.aruco.ArucoDetector(dictionary, parameters)
        self(frame)

    def __call__(self, frame):
        frame[:, :, :] = frame[::-1, ::-1, :]
        h, w = frame.shape[:2]
        middle = np.array(frame.shape[:2][::-1]) * .5
        cv2.circle(frame, np.array(middle, np.int32), 2, (0, 0, 255), 3)
        cv2.circle(frame, np.array((w * .5, h), np.int32), 2, (0, 0, 255), 3)
        corners, ids, _ = self.detector.detectMarkers(frame)

        for id_, point in render(middle):
            cv2.circle(frame, point, 2, (255, 0, 0), 3)
            cv2.putText(frame, str(id_), point, font, .5, (128, 128, 128), 1, cv2.LINE_AA)

        if ids is None:
            print('\rNo tag visible', end='')
            return
        screen_positions = {}
        ids = tuple(i[0] for i in ids)
        for rect, id_ in zip(corners, ids):
            pos = np.array(np.mean(rect[0], axis=0), dtype='int32')
            if id_ not in positions:
                test = find_pos(middle, pos)
                post_test = render_point(middle, np.append(test, (0.,)))
                cv2.circle(frame, post_test, 4, (128, 128, 0), 3)
                cv2.putText(frame, f'  {test[0]:.02f} {test[1]:.02f}', post_test, font, .5, (255, 255, 255), 1, cv2.LINE_AA)
                cv2.circle(frame, pos, 2, (0, 255, 0), 3)
                # cv2.putText(frame, str(id_), pos, font, .5, (255, 255, 255), 2, cv2.LINE_AA)
            else:
                screen_positions[id_] = pos
                # cv2.putText(frame, str(id_), pos, font, .5, (255, 255, 255), 2, cv2.LINE_AA)
                cv2.circle(frame, pos, 2, (0, 255, 0), 3)

        if all(x in ids for x in positions):
            find_physics(screen_positions, middle)
            print(f'\rI can see the board, {ALPHA = :.04f}, {BETA = :.04f}, {OX = :.02f}, {OY = :.02f}, {OZ = :.02f}', end='')
        else:
            print('\rI can\'t see the board', end='')
