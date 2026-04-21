import cv2
import numpy as np

LOWER_RED1 = np.array([0, 120, 120])
UPPER_RED1 = np.array([10, 255, 255])
LOWER_RED2 = np.array([150, 120, 120])
UPPER_RED2 = np.array([180, 255, 255])

LOWER_GREEN = np.array([40, 50, 50])
UPPER_GREEN = np.array([90, 255, 255])

LOWER_BLUE = np.array([100, 100, 60])
UPPER_BLUE = np.array([130, 255, 255])

MIN_COLOR_PIXELS = 50

HOUGH_DP = 1.2
HOUGH_MIN_DIST = 80
HOUGH_PARAM1 = 100
HOUGH_PARAM2 = 80
HOUGH_MIN_RADIUS = 20
HOUGH_MAX_RADIUS = 100


def build_status_panel(frame_shape, circles_count, selected_color, selected_counts):
    panel_h = frame_shape[0]
    panel_w = 380
    panel = np.zeros((panel_h, panel_w, 3), dtype=np.uint8)

    title_color = (80, 220, 255)
    text_color = (235, 235, 235)
    muted_color = (160, 160, 160)

    cv2.putText(panel, "Processing Status", (18, 34),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, title_color, 2)

    lines = [
        f"Frame: {frame_shape[1]}x{frame_shape[0]}",
        f"Circles detected: {circles_count}",
        f"Selected color: {selected_color}",
        "",
        "Selected circle pixel counts:",
        f"RED:   {selected_counts['RED']}",
        f"GREEN: {selected_counts['GREEN']}",
        f"BLUE:  {selected_counts['BLUE']}",
        "",
        f"Min color pixels: {MIN_COLOR_PIXELS}",
        "",
        "Hough params:",
        f"dp={HOUGH_DP}, minDist={HOUGH_MIN_DIST}",
        f"p1={HOUGH_PARAM1}, p2={HOUGH_PARAM2}",
        f"radius={HOUGH_MIN_RADIUS}-{HOUGH_MAX_RADIUS}",
        "",
        "Controls:",
        "ESC: quit"
    ]

    y = 70
    for line in lines:
        color = text_color if line else muted_color
        cv2.putText(panel, line, (18, y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, color, 1, cv2.LINE_AA)
        y += 26

    return panel


def setup_camera(camera_index=0):
    cap = cv2.VideoCapture(camera_index)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    return cap


def detect_color(hsv, mask):
    red_mask = cv2.bitwise_or(
        cv2.inRange(hsv, LOWER_RED1, UPPER_RED1),
        cv2.inRange(hsv, LOWER_RED2, UPPER_RED2)
    )
    green_mask = cv2.inRange(hsv, LOWER_GREEN, UPPER_GREEN)
    blue_mask = cv2.inRange(hsv, LOWER_BLUE, UPPER_BLUE)

    red = cv2.countNonZero(cv2.bitwise_and(red_mask, red_mask, mask=mask))
    green = cv2.countNonZero(cv2.bitwise_and(green_mask, green_mask, mask=mask))
    blue = cv2.countNonZero(cv2.bitwise_and(blue_mask, blue_mask, mask=mask))

    counts = {"RED": red, "GREEN": green, "BLUE": blue}
    color = max(counts, key=counts.get)

    if counts[color] < MIN_COLOR_PIXELS:
        return "UNKNOWN", counts
    return color, counts


def run_detector(camera_index=0):
    cap = setup_camera(camera_index)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        blurred = cv2.GaussianBlur(frame, (5, 5), 0)
        gray = cv2.cvtColor(blurred, cv2.COLOR_BGR2GRAY)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        circles = cv2.HoughCircles(
            gray,
            cv2.HOUGH_GRADIENT,
            dp=HOUGH_DP,
            minDist=HOUGH_MIN_DIST,
            param1=HOUGH_PARAM1,
            param2=HOUGH_PARAM2,
            minRadius=HOUGH_MIN_RADIUS,
            maxRadius=HOUGH_MAX_RADIUS
        )

        circles_count = 0
        selected_color = "NONE"
        selected_counts = {"RED": 0, "GREEN": 0, "BLUE": 0}

        if circles is not None:
            circles = np.uint16(np.around(circles))
            circles_count = len(circles[0])

            for (x, y, r) in circles[0]:
                mask = np.zeros(gray.shape, dtype=np.uint8)
                cv2.circle(mask, (x, y), r, 255, -1)

                color, counts = detect_color(hsv, mask)
                selected_color = color
                selected_counts = counts

                cv2.circle(frame, (x, y), r, (0, 255, 0), 2)
                cv2.putText(frame, color, (x - 40, y - r - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        cv2.imshow("Color Circles", frame)
        status_panel = build_status_panel(
            frame.shape,
            circles_count,
            selected_color,
            selected_counts
        )
        cv2.imshow("Config / Processing", status_panel)

        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    run_detector(camera_index=0)