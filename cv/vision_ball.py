import cv2
import numpy as np
import json
import os

def get_config():
    config_path = os.path.join(os.path.dirname(__file__), "..", "config.json")
    with open(config_path, "r") as conf_json:
        return json.loads(conf_json.read())

global_config = get_config()


# ---------------- COLOR CLASSIFICATION ----------------
def classify_color(hsv_img, x, y, r):
    cv_conf = global_config["cv"]

    mask = np.zeros(hsv_img.shape[:2], dtype=np.uint8)
    cv2.circle(mask, (x, y), int(r), 255, -1)

    red_lower1 = np.array(cv_conf["hsv"]["red"]["lower1"])
    red_upper1 = np.array(cv_conf["hsv"]["red"]["upper1"])
    red_lower2 = np.array(cv_conf["hsv"]["red"]["lower2"])
    red_upper2 = np.array(cv_conf["hsv"]["red"]["upper2"])

    green_lower = np.array(cv_conf["hsv"]["green"]["lower"])
    green_upper = np.array(cv_conf["hsv"]["green"]["upper"])

    blue_lower = np.array(cv_conf["hsv"]["blue"]["lower"])
    blue_upper = np.array(cv_conf["hsv"]["blue"]["upper"])

    red_mask = cv2.bitwise_or(
        cv2.inRange(hsv_img, red_lower1, red_upper1),
        cv2.inRange(hsv_img, red_lower2, red_upper2)
    )

    green_mask = cv2.inRange(hsv_img, green_lower, green_upper)
    blue_mask = cv2.inRange(hsv_img, blue_lower, blue_upper)

    red_count = cv2.countNonZero(cv2.bitwise_and(red_mask, red_mask, mask=mask))
    green_count = cv2.countNonZero(cv2.bitwise_and(green_mask, green_mask, mask=mask))
    blue_count = cv2.countNonZero(cv2.bitwise_and(blue_mask, blue_mask, mask=mask))

    counts = {"RED": red_count, "GREEN": green_count, "BLUE": blue_count}

    color = max(counts, key=counts.get)

    if counts[color] < 20:
        return "UNKNOWN"

    return color


# ---------------- CAMERA VERSION ----------------
def run_camera(camera_index=1):
    cap = cv2.VideoCapture(camera_index)

    if not cap.isOpened():
        print("Camera not opened")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # resize
        frame = cv2.resize(
            frame,
            (global_config["cv"]["camera"]["width"],
             global_config["cv"]["camera"]["height"])
        )

        blurred = cv2.GaussianBlur(
            frame,
            (global_config["cv"]["preprocess"]["blur_kernel"],
             global_config["cv"]["preprocess"]["blur_kernel"]),
            2
        )

        gray = cv2.cvtColor(blurred, cv2.COLOR_BGR2GRAY)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        circles = cv2.HoughCircles(
            gray,
            cv2.HOUGH_GRADIENT,
            dp=global_config["cv"]["hough"]["dp"],
            minDist=global_config["cv"]["hough"]["minDist"],
            param1=global_config["cv"]["hough"]["param1"],
            param2=global_config["cv"]["hough"]["param2"],
            minRadius=global_config["cv"]["hough"]["minRadius"],
            maxRadius=global_config["cv"]["hough"]["maxRadius"]
        )

        if circles is not None:
            circles = np.uint16(np.around(circles))

            for (x, y, r) in circles[0]:
                color = classify_color(hsv, x, y, r)

                # draw
                cv2.circle(frame, (x, y), r, (0, 255, 0), 2)
                cv2.circle(frame, (x, y), 3, (0, 0, 255), -1)

                cv2.putText(
                    frame,
                    color,
                    (x - 40, y - r - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (255, 255, 255),
                    2
                )

                print(f"Detected: {color} at ({x},{y}) r={r}")

        cv2.imshow("Camera Detection", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


# ---------------- RUN ----------------
run_camera(1)