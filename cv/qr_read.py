import cv2

def detect_qr(frame, detector):
    data, bbox, _ = detector.detectAndDecode(frame)

    if bbox is not None:
        # draw box
        pts = bbox[0].astype(int)
        for i in range(len(pts)):
            cv2.line(frame, tuple(pts[i]), tuple(pts[(i+1) % len(pts)]), (0, 255, 0), 2)

        if data:
            cv2.putText(frame, data, (20, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1,
                        (0, 255, 0), 2)
            return data, frame
        
def qr_data():
    cap = cv2.VideoCapture(0)  # change index if needed
    detector = cv2.QRCodeDetector()

    last_data = None

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        data, frame = detect_qr(frame, detector)

    return data

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    qr_data()