import numpy as np
import cv2
import scipy
from frechetdist import frdist

dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
parameters = cv2.aruco.DetectorParameters()
detector = cv2.aruco.ArucoDetector(dictionary, parameters)


IDS = 20, 21, 23, 22
real_positions = {
    21: np.array([0., 0., 0.]),
    20: np.array([86., 0., 0.]),
    23: np.array([0., 185., 0.]),
    22: np.array([86., 185., 0.])
}


def detect(frame):
    corners, ids, _ = detector.detectMarkers(frame)
    return zip((i for i, in ids), (rect for rect, in corners)) if ids is not None else ()


class Camera:
    middle = np.zeros((2,), np.int32)
    alpha, beta, x, y, z, cos_a, cos_b, sin_a, sin_b = 0., 1.5, 40., -20., 110., 0., 0., 0., 0.
    vec, xp, yp = np.zeros((3, 3), float)
    kfp: float
    old_dist = None

    # scipy.minimize bounds:
    #         |        alpha        |  |   beta    |  |    x   |  |    y     |  |    z    |
    bounds = ((-np.pi / 4, np.pi / 4), (0., np.pi/2), (0., 100.), (-90., -10.), (70., 130.))

    def compute_vars(self):
        self.cos_a, self.cos_b, self.sin_a, self.sin_b = (
            np.cos(self.alpha), np.cos(self.beta), np.sin(self.alpha), np.sin(self.beta)
        )
        self.vec = np.array((self.sin_a * self.cos_b, self.cos_a * self.cos_b, -self.sin_b))
        self.xp = np.array((self.cos_a, -self.sin_a, 0.))
        self.yp = np.cross(self.xp, self.vec)

    def next_frame(self):
        pass

    def jacobian(self, height=0.):
        def j(pos):
            vec = np.append(pos, (height,)) - (self.x, self.y, self.z)
            dotv, dotx, doty = np.dot(vec, self.vec), np.dot(vec, self.xp), np.dot(vec, self.yp)
            return self.kfp * np.array([
                [
                    self.cos_a * dotv - self.sin_a * self.cos_b * dotx,
                    -self.sin_a * dotv - self.cos_a * self.cos_b * dotx
                ], [
                    -(self.sin_a * self.sin_b * dotv - self.sin_a * self.cos_b * doty),
                    -(self.cos_a * self.sin_b * dotv - self.cos_a * self.cos_b * doty)
                ]
            ]
            ) / dotv ** 2

        return j

    def pre_render(self, point):
        vec = point - (self.x, self.y, self.z)
        return np.dot((self.xp, self.yp), vec) * self.kfp / np.dot(self.vec, vec)

    def render(self, point):
        return np.int32(self.pre_render(point) * (1, -1) + self.middle)

    def get_position(self, corners, height=0.):
        # centered tag version
        pos = (np.int32(np.mean(corners, axis=0)) - self.middle) * (1, -1)

        def function(point):
            return self.pre_render(np.append(point, (height,))) - pos

        return scipy.optimize.fsolve(function, np.array((50., 50.)), fprime=self.jacobian(height))

    def find_physics(self, screen_positions):
        screen_curve = tuple(screen_positions[id_] for id_ in IDS)

        def dist(values):
            alpha, beta, x, y, z = values
            cos_a, sin_a = np.cos(alpha), np.sin(alpha)
            cos_b, sin_b = np.cos(beta), np.sin(beta)
            v, xp = np.array([sin_a * cos_b, cos_a * cos_b, -sin_b]), np.array([cos_a, -sin_a, 0.])
            yp = np.cross(xp, v)

            curve = []
            for id_ in IDS:
                vector = real_positions[id_] - (x, y, z)
                curve.append(np.int32((self.kfp * np.dot((xp, yp), vector) / np.dot(vector, v)) * (1, -1) + self.middle))

            return frdist(screen_curve, curve)
        vec = scipy.optimize.minimize(
            dist, np.array((self.alpha, self.beta, self.x, self.y, self.z)), method='Powell', bounds=self.bounds
        ).x
        return dist(vec), vec

    def update_physics(self, screen_positions):
        tmp_dist = frdist(
            tuple(self.render(real_positions[id_]) for id_ in IDS),
            tuple(screen_positions[id_] for id_ in IDS)
        )
        if self.old_dist is None or self.old_dist > 5. or tmp_dist > 10.:
            new, new_vec = self.find_physics(screen_positions)
            if self.old_dist is None or self.old_dist > new:
                self.old_dist = new
                self.alpha, self.beta, self.x, self.y, self.z = new_vec
                self.compute_vars()
                return True
        return False


class LogitechCamera(Camera):
    resolution = 1920, 1080
    middle = np.int32(np.array(.5) * resolution)

    # gain de transformation cm -> pixel
    kfp = 1152.0  # 1152.

    def __init__(self, port):
        self.vid = cv2.VideoCapture(port, cv2.CAP_DSHOW)
        self.vid.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution[0])
        self.vid.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution[1])
        self.compute_vars()

    def next_frame(self):
        ret, frame = self.vid.read()
        if ret:
            return frame[::-1, ::-1, :]
        return None
