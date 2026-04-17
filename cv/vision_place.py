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

    if counts[color] < 50:
        return "UNKNOWN"
    return color


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
            dp=1.2,
            minDist=80,
            param1=100,
            param2=70,
            minRadius=20,
            maxRadius=150
        )

        if circles is not None:
            circles = np.uint16(np.around(circles))

            for (x, y, r) in circles[0]:
                mask = np.zeros(gray.shape, dtype=np.uint8)
                cv2.circle(mask, (x, y), r, 255, -1)

                color = detect_color(hsv, mask)

                cv2.circle(frame, (x, y), r, (0, 255, 0), 2)
                cv2.putText(frame, color, (x - 40, y - r - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        cv2.imshow("Color Circles", frame)

        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    run_detector(camera_index=1)