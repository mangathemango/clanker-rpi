import cv2
import numpy as np
from collections import deque
from dataclasses import dataclass
from typing import Optional

# ---------------- CONFIG ----------------
CAMERA_INDEX = 0

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


@dataclass
class BoundaryLine:
    x1: Optional[int] = None
    y1: Optional[int] = None
    x2: Optional[int] = None
    y2: Optional[int] = None


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
# orientation: straight=bottom-up, upside down=top-down, left=left-to-right, right=right-to-left
def get_boundary_line(mask, orientation):
    h, w = mask.shape

    points = []

    if orientation == "straight":
        scan_axis = "col"
        u = -1
    elif orientation == "upside_down":
        scan_axis = "col"
        u = 0
    elif orientation == "left":
        scan_axis = "row"
        u = 0
    elif orientation == "right":
        scan_axis = "row"
        u = -1
    else:
        raise ValueError(f"Unknown orientation: {orientation}")

    if scan_axis == "col":
        # scan each column → find boundary from top or bottom
        for x in range(0, w, 5):  # step=5 for speed + stability
            column = mask[:, x]
            ys = np.where(column > 0)[0]

            if len(ys) > 0:
                y = ys[u]
                points.append((x, y))
    else:
        # scan each row → find boundary from left or right
        for y in range(0, h, 5):  # step=5 for speed + stability
            row = mask[y, :]
            xs = np.where(row > 0)[0]

            if len(xs) > 0:
                x = xs[u]
                points.append((x, y))

    if len(points) < 10:
        return None, None

    pts = np.array(points)

    # fit line using least squares
    vx, vy, x0, y0 = cv2.fitLine(pts, cv2.DIST_L2, 0, 0.01, 0.01)

    return (vx, vy, x0, y0), pts


def get_region_grid(mask):
    h, w = mask.shape
    row_height = h // 3
    col_width = w // 3

    grid = []
    for i in range(3):
        row = []
        for j in range(3):
            start_row = i * row_height
            end_row = (i + 1) * row_height if i < 2 else h
            start_col = j * col_width
            end_col = (j + 1) * col_width if j < 2 else w
            region = mask[start_row:end_row, start_col:end_col]
            row.append(cv2.countNonZero(region))
        grid.append(row)

    return grid


def line_to_boundary(line):
    vx, vy, x0, y0 = line
    x1 = int(x0[0] - vx[0] * 1000)
    y1 = int(y0[0] - vy[0] * 1000)
    x2 = int(x0[0] + vx[0] * 1000)
    y2 = int(y0[0] + vy[0] * 1000)
    return BoundaryLine(x1=x1, y1=y1, x2=x2, y2=y2)


def get_line_guard_state(frame, color="gray", orientation="straight"):
    
    """
    param: \n
    frame from cap.read() \n
    colour = gray/yellow \n
    orientation = straight/upside_down/left/right
    """
    if color == "yellow":
        mask = get_yellow_mask(frame)
    elif color == "gray":
        mask = get_gray_mask(frame)
    else:
        raise ValueError(f"Unknown color: {color}")

    pixels = get_region_grid(mask)
    line, _ = get_boundary_line(mask, orientation)

    if line is not None:
        raw_angle = line_to_angle(line)
        angle = smooth_angle(raw_angle)
        boundary = line_to_boundary(line)
    else:
        angle = 0
        boundary = BoundaryLine()

    return angle, pixels, boundary


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
    row_height = h // 3
    col_width = w // 3
    
    regions = []
    for i in range(3):  # rows
        for j in range(3):  # columns
            start_row = i * row_height
            end_row = (i + 1) * row_height if i < 2 else h
            start_col = j * col_width
            end_col = (j + 1) * col_width if j < 2 else w
            region = mask[start_row:end_row, start_col:end_col]
            count = cv2.countNonZero(region)
            regions.append(count)
    
    # Aggregate into left, center, right (summing columns)
    left = regions[0] + regions[3] + regions[6]  # top-left + mid-left + bottom-left
    center = regions[1] + regions[4] + regions[7]  # top-center + mid-center + bottom-center
    right = regions[2] + regions[5] + regions[8]  # top-right + mid-right + bottom-right
    
    return left, center, right


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


def draw_debug(frame, mask, action):
    h, w, _ = frame.shape
    
    # Existing vertical lines
    cv2.line(frame, (w // 3, 0), (w // 3, h), (255, 0, 0), 2)
    cv2.line(frame, (2 * w // 3, 0), (2 * w // 3, h), (255, 0, 0), 2)
    
    # New horizontal lines for 3x3 grid
    cv2.line(frame, (0, h // 3), (w, h // 3), (255, 0, 0), 2)
    cv2.line(frame, (0, 2 * h // 3), (w, 2 * h // 3), (255, 0, 0), 2)
    
    # Optional: Display individual 9 region counts (compute regions here or pass as param)
    # For brevity, assuming regions are computed similarly to analyze_regions
    row_height = h // 3
    col_width = w // 3
    regions = []
    for i in range(3):
        for j in range(3):
            start_row = i * row_height
            end_row = (i + 1) * row_height if i < 2 else h
            start_col = j * col_width
            end_col = (j + 1) * col_width if j < 2 else w
            region = mask[start_row:end_row, start_col:end_col]
            count = cv2.countNonZero(region)
            regions.append(count)
            # Display each count in its region
            text_x = start_col + 10
            text_y = start_row + 30
            cv2.putText(frame, f"{count}", (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
    
    # Existing action display
    cv2.putText(frame, f"Action: {action}", (10, h - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    
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
        line, pts = get_boundary_line(mask, "straight")

        if line is not None:
            raw_angle = line_to_angle(line)
            angle = smooth_angle(raw_angle)
        else:
            angle = 0

        action = decide_action(left, center, right, angle)

        # draw fitted line
        draw_line(frame, line)

        print(f"Angle:{angle:.2f} -> {action}")

        draw_debug(frame, mask, action)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    run()