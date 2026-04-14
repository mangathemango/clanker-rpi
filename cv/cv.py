import sys

sys.path.append("..")

import cv2
import numpy as np
from server.config import global_config

def classify_color(hsv_img, x, y, r):
    global global_config
    cv_conf = global_config["cv"]
    for i in range(100):
        # Create mask for this circle
        mask = np.zeros(hsv_img.shape[:2], dtype=np.uint8)
        cv2.circle(mask, (x, y), int(r * (0.5 + float(i)/10)), 255, -1)

        # HSV ranges (tuned for your case)
        red_lower1 = np.array([cv_conf["hsv"]["red"]["lower1"], 100, 100])
        red_upper1 = np.array(cv_conf["hsv"]["red"]["upper1"])
        red_lower2 = np.array(cv_conf["hsv"]["red"]["lower2"])
        red_upper2 = np.array(cv_conf["hsv"]["red"]["upper2"])

        green_lower = np.array(cv_conf["hsv"]["green"]["lower"])
        green_upper = np.array(cv_conf["hsv"]["green"]["upper"])

        blue_lower = np.array(cv_conf["hsv"]["blue"]["lower"])
        blue_upper = np.array(cv_conf["hsv"]["blue"]["upper"])

        # Create masks
        red_mask = cv2.bitwise_or(
            cv2.inRange(hsv_img, red_lower1, red_upper1),
            cv2.inRange(hsv_img, red_lower2, red_upper2)
        )

        green_mask = cv2.inRange(hsv_img, green_lower, green_upper)
        blue_mask = cv2.inRange(hsv_img, blue_lower, blue_upper)

        # Count pixels inside circle
        red_count = cv2.countNonZero(cv2.bitwise_and(red_mask, red_mask, mask=mask))
        green_count = cv2.countNonZero(cv2.bitwise_and(green_mask, green_mask, mask=mask))
        blue_count = cv2.countNonZero(cv2.bitwise_and(blue_mask, blue_mask, mask=mask))

        counts = {"RED": red_count, "GREEN": green_count, "BLUE": blue_count}
        print(counts)
        color = max(counts, key=counts.get)

        if counts[color] < 20:
            continue
        return color
    return "UNKNOWN"


def detect_circles_and_colors(input_path, output_path):
    global global_config
    img = cv2.imread(input_path)
    output = img.copy()

    # Resize for speed
    img = cv2.resize(img, (global_config["cv"]["camera"]["width"], global_config["cv"]["camera"]["height"]))
    output = cv2.resize(output, (global_config["cv"]["camera"]["width"], global_config["cv"]["camera"]["height"]))

    blurred = cv2.GaussianBlur(img, (global_config["cv"]["preprocess"]["blur_kernel"], global_config["cv"]["preprocess"]["blur_kernel"]), 2)
    gray = cv2.cvtColor(blurred, cv2.COLOR_BGR2GRAY)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

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

            # Draw circle
            cv2.circle(output, (x, y), r, (0, 255, 0), 2)
            cv2.circle(output, (x, y), 3, (0, 0, 255), -1)

            # Draw label
            cv2.putText(
                output,
                color,
                (x - 40, y - r - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2
            )

    cv2.imwrite(output_path, output)
    print(f"Saved to {output_path}")


# Run it
detect_circles_and_colors("image.jpg", "output.jpg")