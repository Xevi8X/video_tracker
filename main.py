import cv2
import numpy as np
from video_tracker import VideoTracker, TrackingState

# Input setting
# cap = cv2.VideoCapture(0)
cap = cv2.VideoCapture("rtsp://localhost:8554/example")
if not cap.isOpened():
    print("Could not open webcam")
    exit()
for _ in range(5):    
    ret, frame = cap.read()
    if not ret:
        print("Failed to read")
        cap.release()
        exit()

frame_size = (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
print(f"Frame size: {frame_size[0]}x{frame_size[1]}")

# bbox = cv2.selectROI("Select ROI", frame, fromCenter=False, showCrosshair=False)
# cv2.destroyWindow("Select ROI")

tracker = VideoTracker(frame_size)
# tracker.start_tracking(frame, bbox)

last_frame = None
click_pos = None
a = 40
correction_diff = 3

def mouse_event(event, x, y, flags, param):
    global click_pos
    if event == cv2.EVENT_LBUTTONDOWN:
        click_pos = (x,y)
        # print(f'Clicked {x}, {y}')

cv2.namedWindow("Tracking")
cv2.setMouseCallback("Tracking", mouse_event)

while True:
    # Mouse handling
    if not click_pos is None and not last_frame is None :
        x = np.clip(click_pos[0], a, frame_size[0] - a)
        y = np.clip(click_pos[1], a, frame_size[1] - a)
        tracker.start_tracking(last_frame, (x - a, y - a, 2*a, 2*a))
        click_pos = None

    # Keyboard handling
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == 81:  # Left arrow key
        tracker.correct_target(-correction_diff, 0)
    elif key == 82:  # Up arrow key
        tracker.correct_target(0, -correction_diff)
    elif key == 83:  # Right arrow key
        tracker.correct_target(correction_diff, 0)
    elif key == 84:  # Down arrow key
        tracker.correct_target(0, correction_diff)

    # Read frame
    ret, frame = cap.read()
    if not ret:
        break
    last_frame = frame

    state, bbox = tracker.update_tracking(frame)
    print(bbox)

    if state == TrackingState.TRACKING:
        color = (0, 255, 0)
    elif state == TrackingState.SEARCHING:
        color = (0, 255, 255)
    else:
        color = None
    if color:
        p1 = (int(bbox[0]), int(bbox[1]))
        p2 = (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3]))
        cv2.rectangle(frame, p1, p2, color, 2, 1)

    cv2.imshow("Tracking", frame)

cap.release()
cv2.destroyAllWindows()
