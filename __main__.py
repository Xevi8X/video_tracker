import cv2
import numpy as np
from video_tracker import VideoTracker, TrackingState

if __name__ == "__main__":
    ### Input setting
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


    ### Tracker setting
    tracker = VideoTracker(frame_size)

    last_frame = None
    click_pos = None
    a = 40
    correction_diff = 5
    resize_diff = 5
    cv2.namedWindow("Tracking", cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty("Tracking", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    def mouse_event(event, x, y, flags, param):
        global click_pos
        if event == cv2.EVENT_LBUTTONDOWN:
            click_pos = (x,y)
            # print(f'Clicked {x}, {y}')

    cv2.setMouseCallback("Tracking", mouse_event)


    ### Optional: Select ROI
    # bbox = cv2.selectROI("Select ROI", frame, fromCenter=False, showCrosshair=False)
    # cv2.destroyWindow("Select ROI")
    # tracker.start_tracking(frame, bbox)


    ### Main loop
    while True:
        # Mouse handling
        if not click_pos is None and not last_frame is None :
            x = np.clip(click_pos[0], a, frame_size[0] - a)
            y = np.clip(click_pos[1], a, frame_size[1] - a)
            tracker.start_tracking(last_frame, (x - a, y - a, 2*a, 2*a))
            click_pos = None

        # Keyboard handling
        key = cv2.waitKey(1) & 0xFF
        if key == 27:  # Esc key
            break
        elif key == ord('q'):
            tracker.resize_target(-resize_diff, -resize_diff, -resize_diff, -resize_diff)
        elif key == ord('e'):
            tracker.resize_target(resize_diff, resize_diff, resize_diff, resize_diff)
        elif key in [81, ord('a')]:  # Left arrow key
            tracker.correct_target(-correction_diff, 0)
        elif key in [82, ord('w')]:  # Up arrow key
            tracker.correct_target(0, -correction_diff)
        elif key in [83, ord('d')]:  # Right arrow key
            tracker.correct_target(correction_diff, 0)
        elif key in [84, ord('s')]:  # Down arrow key
            tracker.correct_target(0, correction_diff)

        # Read frame
        ret, frame = cap.read()
        if not ret:
            break
        last_frame = frame

        state, bbox = tracker.update_tracking(frame)

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
