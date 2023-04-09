import numpy as np
import cv2
import scipy
from frechetdist import frdist
import pyrealsense2 as rs


dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
parameters = cv2.aruco.DetectorParameters()

parameters_attributes = (
    'adaptiveThreshConstant',
    'adaptiveThreshWinSizeMax',
    'adaptiveThreshWinSizeMin',
    'adaptiveThreshWinSizeStep',
    'aprilTagCriticalRad',
    'aprilTagDeglitch',
    'aprilTagMaxLineFitMse',
    'aprilTagMaxNmaxima',
    'aprilTagMinClusterPixels',
    'aprilTagMinWhiteBlackDiff',
    'aprilTagQuadDecimate',
    'aprilTagQuadSigma',
    'cornerRefinementMaxIterations',
    'cornerRefinementMethod',
    'cornerRefinementMinAccuracy',
    'cornerRefinementWinSize',
    'detectInvertedMarker',
    'errorCorrectionRate',
    'markerBorderBits',
    'maxErroneousBitsInBorderRate',
    'maxMarkerPerimeterRate',
    'minCornerDistanceRate',
    'minDistanceToBorder',
    'minMarkerDistanceRate',
    'minMarkerLengthRatioOriginalImg',
    'minMarkerPerimeterRate',
    'minOtsuStdDev',
    'minSideLengthCanonicalImg',
    'perspectiveRemoveIgnoredMarginPerCell',
    'perspectiveRemovePixelPerCell',
    'polygonalApproxAccuracyRate',
    'readDetectorParameters',
    'useAruco3Detection',
    'writeDetectorParameters'
)
# parameters.minMarkerPerimeterRate = 0.003
detector = cv2.aruco.ArucoDetector(dictionary, parameters)


IDS = 20, 21, 23, 22
SE, SW, NW, NE = IDS
DX, DY = 86., 185.
real_positions = {
    21: np.array([0., 0., 0.]),
    20: np.array([DX, 0., 0.]),
    23: np.array([0., DY, 0.]),
    22: np.array([DX, DY, 0.])
}


def cross_ratio(a, b, c, d):
    vec = b - a
    return np.dot(a - c, vec) * np.dot(b - d, vec) / (np.dot(b - c, vec) * np.dot(a - d, vec))


def find_coordinate(point, zero, zero_real, tag_screen, tag_real, infinity):
    return cross_ratio(point, tag_screen, zero, infinity) * np.sum((tag_real - zero_real) ** 2) ** .5


def line_intersection(line1_p1, line1_p2, line2_p1, line2_p2):
    vec1, vec2 = np.float_(line1_p2 - line1_p1), np.float_(line2_p2 - line2_p1)
    return line2_p1 + vec2 * np.cross(vec1, np.float_(line2_p1 - line1_p1)) / np.cross(vec2, vec1)


def get_center(corners):
    return line_intersection(corners[0], corners[2], corners[1], corners[3])


def detect(frame):
    corners, ids, _ = detector.detectMarkers(frame)
    return zip((i for i, in ids), (np.int32(rect) for rect, in corners)) if ids is not None else ()


class Camera:
    resolution = (0, 0)
    middle = np.zeros((2,), np.int32)
    alpha, beta, x, y, z, cos_a, cos_b, sin_a, sin_b = 0.1, .6, 60., -50., 100., 0., 0., 0., 0.
    vec, xp, yp = np.zeros((3, 3), float)
    kfp: float
    old_dist = None
    anchor_tag_render: dict
    error_sensitivity: float
    movement_sensitivity: float
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

    def find_physics_brute_force(self, screen_positions):
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

    def find_physics_cross_ratio(self, screen_positions):
        west_line = screen_positions[SW], screen_positions[NW]
        east_line = screen_positions[SE], screen_positions[NE]
        north_line = screen_positions[NW], screen_positions[NE]
        south_line = screen_positions[SW], screen_positions[SE]

        y_infinity = line_intersection(*west_line, *east_line)
        infinity_line = y_infinity, y_infinity + (500., 0.)

        x_infinity = line_intersection(*south_line, *infinity_line)

        middle_line = self.middle, self.middle * (1., 0.)
        north_intersection = line_intersection(*north_line, *middle_line)
        south_intersection = line_intersection(*south_line, *middle_line)
        x1 = find_coordinate(north_intersection, screen_positions[NW], real_positions[NW], screen_positions[NE], real_positions[NE], x_infinity)
        x0 = find_coordinate(south_intersection, screen_positions[SW], real_positions[SW], screen_positions[SE], real_positions[SE], x_infinity)
        tan_alpha = (x1 - x0) / DY

        self.alpha = np.arctan(tan_alpha)

        # allows to avoid alpha = 0 problems
        diagonal_infinity = (line_intersection(*infinity_line, screen_positions[SW], screen_positions[NE]) - self.middle) * (1, -1)
        k = DY / DX

        # print(f'\r{diagonal_infinity = } {tan_alpha = } {(diagonal_infinity[1] / diagonal_infinity[0]) = } {(k + tan_alpha) / (1 - k * tan_alpha) =}', end='')
        # sin_beta = (diagonal_infinity[1] / diagonal_infinity[0]) * (1 - k * tan_alpha) / (k + tan_alpha)
        # self.beta = np.arcsin(sin_beta)
        tan_beta = (self.middle[1] - y_infinity[1]) / self.kfp
        self.beta = np.arctan(tan_beta)

        # self.kfp = (1 - sin_beta ** 2) ** .5 * (self.middle[1] - y_infinity[1])
        self.compute_vars()

        west_intersection_oc = line_intersection(*west_line, self.middle, x_infinity)
        south_intersection_oc = line_intersection(*south_line, self.middle, y_infinity)
        self.optic_center = (
            find_coordinate(south_intersection_oc, screen_positions[SW], real_positions[SW], screen_positions[SE], real_positions[SE], x_infinity),
            find_coordinate(west_intersection_oc, screen_positions[SW], real_positions[SW], screen_positions[NW], real_positions[NW], y_infinity),
            0.
        )

        def render_dist(t):
            res = 0.
            for id_ in IDS:
                vec = real_positions[id_] - self.optic_center + t[0] * self.vec
                res += np.sum((np.dot((self.xp, self.yp), vec) * self.kfp / np.dot(self.vec, vec) * (1, -1) + self.middle - screen_positions[id_]) ** 2)
            return res

        t = scipy.optimize.minimize(render_dist, np.array((100.,))).x
        self.x, self.y, self.z = np.array(self.optic_center) - t[0] * self.vec

    def update_physics(self, screen_positions):
        tmp_dist = frdist(
            tuple(self.render(real_positions[id_]) for id_ in IDS),
            tuple(screen_positions[id_] for id_ in IDS)
        )
        if self.old_dist is None or self.old_dist > self.error_sensitivity or tmp_dist > self.movement_sensitivity:
            new, new_vec = self.find_physics_brute_force(screen_positions)
            self.old_dist = tmp_dist
            if self.old_dist is None or self.old_dist > new:
                self.old_dist = new
                self.alpha, self.beta, self.x, self.y, self.z = new_vec
                self.compute_vars()
                return True
        return False


class LogitechCamera(Camera):
    resolution = 1920, 1080
    middle = np.int32(np.array(.5) * resolution)

    error_sensitivity = 5.
    movement_sensitivity = 15.

    # gain de transformation cm -> pixel
    kfp = 1152.0  # 1152.

    def __init__(self, port):
        self.vid = cv2.VideoCapture(port, cv2.CAP_DSHOW)
        self.vid.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution[0])
        self.vid.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution[1])
        self.compute_vars()
        self.anchor_tag_render = {}

    def next_frame(self):
        ret, frame = self.vid.read()
        if ret:
            return frame[::-1, ::-1, :]
        return None


class RealSense(Camera):
    resolution = 640, 480
    middle = np.int32(np.array(.5) * resolution)
    alpha, beta, x, y, z = -0.0412, 0.700, 35., -63.25, 105
    kfp = 589.  # test_value

    error_sensitivity = 8.
    movement_sensitivity = 12.

    def __init__(self):
        self.pipeline = rs.pipeline()
        config = rs.config()
        config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
        self.pipeline.start(config)
        self.anchor_tag_render = {}
        self.compute_vars()

    def next_frame(self):
        frame = self.pipeline.wait_for_frames().get_color_frame()
        return np.asanyarray(frame.get_data()) if frame else None
