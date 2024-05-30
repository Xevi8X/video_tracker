import cv2
from enum import Enum

class TrackingState(Enum):
    TRACKING = 1
    SEARCHING = 2
    TARGET_LOST = 3

class VideoTracker:

    def __init__(self):
        self.__create_tracker()
        self.cap = cv2.VideoCapture(0)
        self.bbox = None
        self.search_limit = 60

    def start_tracking(self, frame, bbox):
        self.searching_counter = 0
        self.last_bbox = bbox
        self.tracker.init(frame, bbox)
        return self.last_bbox

    def update_tracking(self, frame):
        result, bbox = self.tracker.update(frame)
        if not result:
            self.searching_counter += 1

            if self.searching_counter > self.search_limit:
                return TrackingState.TARGET_LOST, None

            return TrackingState.SEARCHING, self.last_bbox

        self.searching_counter = 0
        self.last_bbox = bbox
        return TrackingState.TRACKING, bbox

    def __create_tracker(self):
        # self.tracker = cv2.legacy.TrackerMOSSE_create()
        self.tracker = cv2.legacy.TrackerKCF_create()
        # self.tracker = cv2.legacy.TrackerCSRT_create()
        # self.tracker = cv2.legacy.TrackerBoosting_create()
        # self.tracker = cv2.legacy.TrackerMedianFlow_create()
        # self.tracker = cv2.legacy.TrackerTLD_create()
        # self.tracker = cv2.legacy.TrackerMIL_create()
        # self.tracker = cv2.legacy.TrackerGOTURN_create()



# Camera setting
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Could not open webcam")
    exit()
for _ in range(5):    
    ret, frame = cap.read()
    if not ret:
        print("Failed to read from webcam")
        cap.release()
        exit()

bbox = cv2.selectROI("Select ROI", frame, fromCenter=False, showCrosshair=False)
cv2.destroyWindow("Select ROI")

tracker = VideoTracker()
tracker.start_tracking(frame, bbox)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    state, bbox = tracker.update_tracking(frame)

    if state == TrackingState.TRACKING:
        color = (0, 255, 0)
    elif state == TrackingState.SEARCHING:
        color = (0, 255, 255)
    elif state == TrackingState.TARGET_LOST:
        color = None
    else:
        color = None

    if color:
        p1 = (int(bbox[0]), int(bbox[1]))
        p2 = (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3]))
        cv2.rectangle(frame, p1, p2, color, 2, 1)

    cv2.imshow("Tracking", frame)

    # Keyboard handling
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
