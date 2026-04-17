import cv2

def detect_qr(frame, detector):
    data, bbox, _ = detector.detectAndDecode(frame)

    if bbox is not None:
        pts = bbox[0].astype(int)

        for i in range(len(pts)):
            cv2.line(frame, tuple(pts[i]), tuple(pts[(i+1) % len(pts)]), (0, 255, 0), 2)

    if data:
        cv2.putText(frame, data, (20, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1,
                    (0, 255, 0), 2)
        return data, frame

    return None, frame


def qr_data(camera_index=0):
    cap = cv2.VideoCapture(camera_index)
    detector = cv2.QRCodeDetector()

    last_data = None

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Camera error")
            break

        data, frame = detect_qr(frame, detector)

        if data and data != last_data:
            last_data = data

            break


    cap.release()

    return last_data


if __name__ == "__main__":
    result = qr_data(0)
    print("Final QR:", result)