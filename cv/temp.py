import cv2
import numpy as np

# Create a window
cv2.namedWindow("Trackbars")

# Dummy function for trackbars
def nothing(x):
    pass

# Create trackbars for HSV range
cv2.createTrackbar("H Lower", "Trackbars", 0, 179, nothing)
cv2.createTrackbar("S Lower", "Trackbars", 0, 255, nothing)
cv2.createTrackbar("V Lower", "Trackbars", 0, 255, nothing)

cv2.createTrackbar("H Upper", "Trackbars", 179, 179, nothing)
cv2.createTrackbar("S Upper", "Trackbars", 255, 255, nothing)
cv2.createTrackbar("V Upper", "Trackbars", 255, 255, nothing)

# Mouse callback to print HSV value
def pick_color(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        frame = param
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        pixel = hsv[y, x]
        print(f"Clicked HSV: {pixel}")

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Get trackbar values
    h_l = cv2.getTrackbarPos("H Lower", "Trackbars")
    s_l = cv2.getTrackbarPos("S Lower", "Trackbars")
    v_l = cv2.getTrackbarPos("V Lower", "Trackbars")

    h_u = cv2.getTrackbarPos("H Upper", "Trackbars")
    s_u = cv2.getTrackbarPos("S Upper", "Trackbars")
    v_u = cv2.getTrackbarPos("V Upper", "Trackbars")

    lower = np.array([h_l, s_l, v_l])
    upper = np.array([h_u, s_u, v_u])

    # Create mask
    mask = cv2.inRange(hsv, lower, upper)

    # Show results
    cv2.imshow("Original", frame)
    cv2.imshow("Mask", mask)

    # Set mouse callback (pass frame)
    cv2.setMouseCallback("Original", pick_color, frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()