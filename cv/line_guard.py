import cv2
import numpy as np
from collections import deque

# ---------------- CONFIG ----------------
CAMERA_INDEX = 1

FRAME_WIDTH = 640
FRAME_HEIGHT = 480

YELLOW_LOWER = np.array([15, 10, 60])
YELLOW_UPPER = np.array([40, 80, 210])
GRAY_LOWER = np.array([80, 10, 120])
GRAY_UPPER = np.array([130, 80, 255])

THRESH = 50000

USE_UNDISTORT = False

if USE_UNDISTORT:
    mtx = np.load("camera_matrix.npy")
    dist = np.load("dist_coeffs.npy")

# smoothing buffer (VERY IMPORTANT)
ANGLE_HISTORY = deque(maxlen=5)

# ----------------------------------------


def undistort_frame(frame):
    if not USE_UNDISTORT:
        return frame, frame

    h, w = frame.shape[:2]
    newcameramtx, _ = cv2.getOptimalNewCameraMatrix(mtx, dist, (w, h), 1, (w, h))
    undistorted = cv2.undistort(frame, mtx, dist, None, newcameramtx)
    return frame, undistorted


def crop_center(frame):
    h, w = frame.shape[:2]
    return frame[:, w // 4: 3 * w // 4]


def get_yellow_mask(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, YELLOW_LOWER, YELLOW_UPPER)

    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    return mask

def get_gray_mask(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, GRAY_LOWER, GRAY_UPPER)

    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    return mask


# 🔥 NEW: extract boundary + fit line
def get_boundary_line(mask, color):
    h, w = mask.shape

    points = []

    u = 0
    if(color == "yellow"):
        u = -1
    # scan each column → find FIRST yellow pixel (boundary) from bottom up
    for x in range(0, w, 5):  # step=5 for speed + stability
        column = mask[:, x]
        ys = np.where(column > 0)[0]

        if len(ys) > 0:
            y = ys[u]  # bottom-most boundary
            points.append((x, y))

    if len(points) < 10:
        return None, None

    pts = np.array(points)

    # fit line using least squares
    vx, vy, x0, y0 = cv2.fitLine(pts, cv2.DIST_L2, 0, 0.01, 0.01)

    return (vx, vy, x0, y0), pts


# 🔥 NEW: convert line → angle
def line_to_angle(line):
    vx, vy, _, _ = line
    angle = np.degrees(np.arctan2(vy[0], vx[0]))
    return angle


# 🔥 NEW: smooth angle
def smooth_angle(angle):
    ANGLE_HISTORY.append(angle)
    return sum(ANGLE_HISTORY) / len(ANGLE_HISTORY)


def analyze_regions(mask):
    h, w = mask.shape

    left = mask[:, :w // 3]
    center = mask[:, w // 3:2 * w // 3]
    right = mask[:, 2 * w // 3:]

    return (
        cv2.countNonZero(left),
        cv2.countNonZero(center),
        cv2.countNonZero(right),
    )


def decide_action(left, center, right, angle):
    if center > THRESH:
        return "STOP"

    if angle > 5:
        return "TURN LEFT"
    elif angle < -5:
        return "TURN RIGHT"

    if left > THRESH:
        return "TURN RIGHT"
    elif right > THRESH:
        return "TURN LEFT"
    else:
        return "FORWARD"


def draw_line(frame, line):
    if line is None:
        return

    vx, vy, x0, y0 = line

    h, w, _ = frame.shape

    # extend line across frame
    x1 = int(x0[0] - vx[0] * 1000)
    y1 = int(y0[0] - vy[0] * 1000)
    x2 = int(x0[0] + vx[0] * 1000)
    y2 = int(y0[0] + vy[0] * 1000)

    cv2.line(frame, (x1, y1), (x2, y2), (0, 0, 255), 3)


def draw_debug(frame, mask, action, left, center, right, angle):
    h, w, _ = frame.shape

    # draw region lines
    cv2.line(frame, (w // 3, 0), (w // 3, h), (255, 0, 0), 2)
    cv2.line(frame, (2 * w // 3, 0), (2 * w // 3, h), (255, 0, 0), 2)

    # display counts
    cv2.putText(frame, f"L:{left}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    cv2.putText(frame, f"C:{center}", (w // 3 + 10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    cv2.putText(frame, f"R:{right}", (2 * w // 3 + 10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    cv2.putText(frame, f"Angle:{angle:.3f}", (w // 3 + 10, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

    # display action
    cv2.putText(frame, f"Action: {action}", (10, h - 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

    cv2.imshow("Frame", frame)
    cv2.imshow("Mask", mask)


def run():
    cap = cv2.VideoCapture(CAMERA_INDEX)

    if not cap.isOpened():
        print("Camera not opened")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.resize(frame, (FRAME_WIDTH, FRAME_HEIGHT))

        raw_frame, undistorted = undistort_frame(frame)

        cv2.imshow("Undistorted", undistorted)

        # frame = crop_center(undistorted)

        mask = get_gray_mask(frame)

        left, center, right = analyze_regions(mask)

        # 🔥 boundary line detection
        line, pts = get_boundary_line(mask, "gray")

        if line is not None:
            raw_angle = line_to_angle(line)
            angle = smooth_angle(raw_angle)
        else:
            angle = 0

        action = decide_action(left, center, right, angle)

        # draw fitted line
        draw_line(frame, line)

        print(f"Angle:{angle:.2f} -> {action}")

        draw_debug(frame, mask, action, left, center, right, angle)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    run()