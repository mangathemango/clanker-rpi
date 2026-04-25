import cv2
import numpy as np
import time
from collections import deque

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
HOUGH_MAX_RADIUS = 450

# Tracking/smoothing parameters to reduce frame-to-frame jitter.
TRACK_LOCK_DISTANCE = 45
TRACK_MAX_MISSES = 8
POSITION_SMOOTHING_ALPHA = 0.25
RADIUS_SMOOTHING_ALPHA = 0.25
TRACK_MEDIAN_WINDOW = 7
POSITION_DEADBAND_PX = 3.0
RADIUS_DEADBAND_PX = 2.0


def build_status_panel(frame_shape, circles_count, selected_color, selected_counts, selected_circle_xyz):
    panel_h = frame_shape[0]
    panel_w = 380
    panel = np.zeros((panel_h, panel_w, 3), dtype=np.uint8)

    title_color = (80, 220, 255)
    text_color = (235, 235, 235)
    muted_color = (160, 160, 160)

    cv2.putText(panel, "Processing Status", (18, 34),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, title_color, 2)

    if selected_circle_xyz is None:
        circle_line = "Selected circle (x,y,r): N/A"
    else:
        sx, sy, sr = selected_circle_xyz
        circle_line = f"Selected circle (x,y,r): {sx:.1f}, {sy:.1f}, {sr:.1f}"

    lines = [
        f"Frame: {frame_shape[1]}x{frame_shape[0]}",
        f"Circles detected: {circles_count}",
        circle_line,
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


def get_chosen_circle_color_and_position(camera_index=0, cap=None, warmup_frames=5, sample_frames=12):
    """
    Capture a short burst of frames and return the selected circle color and position.

    Returns:
        (color, (x, y, r)) where position values are floats, or ("NONE", None)
        if no stable circle was found.
    """
    if cap is None:
        cap = setup_camera(camera_index)
        release_cap = True
    else:
        release_cap = False
    tracked_circle = None
    missed_frames = 0
    measurement_history = deque(maxlen=TRACK_MEDIAN_WINDOW)
    last_result = ("NONE", None)

    try:
        total_frames = max(1, int(warmup_frames) + int(sample_frames))

        for _ in range(total_frames):
            ret, frame = cap.read()
            if not ret:
                continue

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

            if circles is not None:
                circles = np.uint16(np.around(circles))
                selected_circle = None

                if tracked_circle is not None:
                    tx, ty, _ = tracked_circle
                    nearby = [
                        c for c in circles[0]
                        if np.hypot(float(c[0]) - tx, float(c[1]) - ty) <= TRACK_LOCK_DISTANCE
                    ]
                    if nearby:
                        selected_circle = min(nearby, key=lambda c: c[2])

                if selected_circle is None:
                    selected_circle = min(circles[0], key=lambda c: c[2])

                x, y, r = map(float, selected_circle)
                measurement_history.append((x, y, r))

                med = np.median(np.array(measurement_history, dtype=np.float32), axis=0)
                mx, my, mr = float(med[0]), float(med[1]), float(med[2])

                if tracked_circle is None:
                    tracked_circle = (mx, my, mr)
                else:
                    px, py, pr = tracked_circle
                    dx = mx - px
                    dy = my - py
                    dr = mr - pr

                    sx = px if abs(dx) < POSITION_DEADBAND_PX else (px + POSITION_SMOOTHING_ALPHA * dx)
                    sy = py if abs(dy) < POSITION_DEADBAND_PX else (py + POSITION_SMOOTHING_ALPHA * dy)
                    sr = pr if abs(dr) < RADIUS_DEADBAND_PX else (pr + RADIUS_SMOOTHING_ALPHA * dr)
                    tracked_circle = (sx, sy, sr)

                missed_frames = 0
            else:
                missed_frames += 1
                if missed_frames > TRACK_MAX_MISSES:
                    tracked_circle = None
                    measurement_history.clear()

            if tracked_circle is not None:
                x, y, r = tracked_circle
                xi, yi, ri = int(round(x)), int(round(y)), int(round(r))

                mask = np.zeros(gray.shape, dtype=np.uint8)
                cv2.circle(mask, (xi, yi), ri, 255, -1)
                color, _ = detect_color(hsv, mask)

                last_result = (color, (x, y, r))

        return last_result
    finally:
        if release_cap:
            cap.release()


def get_chosen_color_and_position_stable(camera_index=0, cap=None, stable_time=0.75,
                                         warmup_frames=5, sample_frames=12,
                                         position_tolerance_px=10.0, radius_tolerance_px=10.0):
    """Return the material color and position only after it stays stable for stable_time seconds."""
    if cap is None:
        cap = setup_camera(camera_index)
        release_cap = True
    else:
        release_cap = False

    stable_started_at = None
    stable_color_position = ("NONE", None)
    previous_position = None

    try:
        while True:
            color, position = get_chosen_circle_color_and_position(
                camera_index=camera_index,
                cap=cap,
                warmup_frames=warmup_frames,
                sample_frames=sample_frames,
            )

            if position is None or color == "NONE":
                stable_started_at = None
                previous_position = None
                continue

            current_time = time.monotonic()
            if previous_position is not None:
                px, py, pr = previous_position
                cx, cy, cr = position
                if (
                    np.hypot(cx - px, cy - py) > position_tolerance_px
                    or abs(cr - pr) > radius_tolerance_px
                ):
                    stable_started_at = current_time
                    stable_color_position = (color, position)
                    previous_position = position
                    continue

            if stable_started_at is None:
                stable_started_at = current_time
                stable_color_position = (color, position)
            elif current_time - stable_started_at >= float(stable_time):
                return stable_color_position

            previous_position = position
    finally:
        if release_cap:
            cap.release()

def run_detector(camera_index=0):
    cap = setup_camera(camera_index)

    stable_color, stable_position = get_chosen_color_and_position_stable(
        camera_index=0,
        cap=cap,
    )
    print(f"Stable detection: color={stable_color}, position={stable_position}")

    tracked_circle = None  # (x, y, r) as floats
    missed_frames = 0
    measurement_history = deque(maxlen=TRACK_MEDIAN_WINDOW)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # --- Processing pipeline ---
        blurred = cv2.GaussianBlur(frame, (5, 5), 0)
        gray = cv2.cvtColor(blurred, cv2.COLOR_BGR2GRAY)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Helpful visualization of preprocessing stages.
        edges = cv2.Canny(gray, 50, 150)
        gray_vis = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
        edges_vis = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
        hsv_vis = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

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
        selected_circle_xyz = None

        if circles is not None:
            circles = np.uint16(np.around(circles))
            circles_count = len(circles[0])

            # Keep lock on a nearby circle to prevent jumping between detections.
            selected_circle = None
            if tracked_circle is not None:
                tx, ty, _ = tracked_circle
                nearby = [
                    c for c in circles[0]
                    if np.hypot(float(c[0]) - tx, float(c[1]) - ty) <= TRACK_LOCK_DISTANCE
                ]
                if nearby:
                    selected_circle = min(nearby, key=lambda c: c[2])

            # Fallback: choose global smallest when no lock candidate exists.
            if selected_circle is None:
                selected_circle = min(circles[0], key=lambda c: c[2])

            x, y, r = map(float, selected_circle)
            measurement_history.append((x, y, r))

            # Median over a short history removes outlier jumps.
            med = np.median(np.array(measurement_history, dtype=np.float32), axis=0)
            mx, my, mr = float(med[0]), float(med[1]), float(med[2])

            # Exponential moving average for a stable "absolute" position.
            if tracked_circle is None:
                tracked_circle = (mx, my, mr)
            else:
                px, py, pr = tracked_circle
                dx = mx - px
                dy = my - py
                dr = mr - pr

                # Deadband keeps tiny pixel noise from moving the overlay.
                sx = px if abs(dx) < POSITION_DEADBAND_PX else (px + POSITION_SMOOTHING_ALPHA * dx)
                sy = py if abs(dy) < POSITION_DEADBAND_PX else (py + POSITION_SMOOTHING_ALPHA * dy)
                sr = pr if abs(dr) < RADIUS_DEADBAND_PX else (pr + RADIUS_SMOOTHING_ALPHA * dr)
                tracked_circle = (sx, sy, sr)

            selected_circle_xyz = tracked_circle

            missed_frames = 0
        else:
            missed_frames += 1
            if missed_frames > TRACK_MAX_MISSES:
                tracked_circle = None
                measurement_history.clear()

        if tracked_circle is not None:
            x, y, r = tracked_circle
            xi, yi, ri = int(round(x)), int(round(y)), int(round(r))
            selected_circle_xyz = (x, y, r)

            mask = np.zeros(gray.shape, dtype=np.uint8)
            cv2.circle(mask, (xi, yi), ri, 255, -1)

            color, counts = detect_color(hsv, mask)
            selected_color = color
            selected_counts = counts

            # Draw the tracked circle on every view so the pipeline stays aligned.
            cv2.circle(frame, (xi, yi), ri, (0, 255, 0), 2)
            cv2.circle(blurred, (xi, yi), ri, (0, 255, 0), 2)
            cv2.circle(gray_vis, (xi, yi), ri, (0, 255, 0), 2)
            cv2.circle(hsv_vis, (xi, yi), ri, (0, 255, 0), 2)
            cv2.circle(edges_vis, (xi, yi), ri, (0, 255, 0), 2)
            cv2.putText(frame, color, (xi - 40, yi - ri - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        # --- Show multiple windows ---
        cv2.imshow("Final Output", frame)
        cv2.imshow("Blurred", blurred)
        cv2.imshow("Grayscale", gray_vis)
        cv2.imshow("HSV (as BGR)", hsv_vis)
        cv2.imshow("Edges (Canny)", edges_vis)

        status_panel = build_status_panel(
            frame.shape,
            circles_count,
            selected_color,
            selected_counts,
            selected_circle_xyz
        )
        cv2.imshow("Config / Processing", status_panel)

        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    run_detector(camera_index=0)