import cv2
import numpy as np

# ---------------- CONFIG ----------------
CAMERA_INDEX = 1

FRAME_WIDTH = 640
FRAME_HEIGHT = 480

# HSV range for yellow (tune if needed)
YELLOW_LOWER = np.array([15, 10, 80])
YELLOW_UPPER = np.array([40, 80, 210])
#rgb(153, 152, 141) , [30, 20, 153]
#898a7c

# pixel threshold to decide danger
THRESH = 500

# ----------------------------------------


def get_yellow_mask(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, YELLOW_LOWER, YELLOW_UPPER)
    return mask


def analyze_regions(mask):
    h, w = mask.shape

    left = mask[:, :w // 3]
    center = mask[:, w // 3:2 * w // 3]
    right = mask[:, 2 * w // 3:]

    left_count = cv2.countNonZero(left)
    center_count = cv2.countNonZero(center)
    right_count = cv2.countNonZero(right)

    return left_count, center_count, right_count


def decide_action(left, center, right):
    #direction could be left, right, forward
    if center > THRESH:
        return "STOP"
    elif left > THRESH:
        return "TURN RIGHT"
    elif right > THRESH:
        return "TURN LEFT"
    else:
        return "FORWARD"


def draw_debug(frame, mask, left, center, right, action):
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

    # display action
    cv2.putText(frame, f"Action: {action}", (10, h - 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

    cv2.imshow("Frame", frame)
    cv2.imshow("Yellow Mask", mask)


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

        mask = get_yellow_mask(frame)

        left, center, right = analyze_regions(mask)

        action = decide_action(left, center, right)

        print(f"L:{left} C:{center} R:{right} -> {action}")

        draw_debug(frame, mask, left, center, right, action)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


# ---------------- RUN ----------------
if __name__ == "__main__":
    run()