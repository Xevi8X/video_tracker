import cv2
from enum import Enum

class TrackingState(Enum):
    UNINITIALIZED   = 0
    TRACKING        = 1
    SEARCHING       = 2
    TARGET_LOST     = 3

class VideoTracker:

    def __init__(self, frame_size):
        self.frame_size = frame_size
        self.__create_tracker()
        self.cap = cv2.VideoCapture(0)
        self.bbox = None
        self.state = TrackingState.UNINITIALIZED

        self.search_frame_limit = 60
        self.minimal_roi_size = 50

    def start_tracking(self, frame, bbox):
        self.searching_counter = 0
        self.last_bbox = bbox
        self.__create_tracker()
        self.tracker.init(frame, bbox)
        self.state = TrackingState.TRACKING
        return self.last_bbox

    def update_tracking(self, frame):
        if self.state == TrackingState.UNINITIALIZED:
            return TrackingState.UNINITIALIZED, None

        self.last_frame = frame
        result, bbox = self.tracker.update(frame)
        if not result or not self.__check_bbox(bbox):
            self.searching_counter += 1

            if self.searching_counter > self.search_frame_limit:
                self.state = TrackingState.UNINITIALIZED
                return TrackingState.TARGET_LOST, None

            self.state = TrackingState.SEARCHING
            return TrackingState.SEARCHING, self.last_bbox

        self.searching_counter = 0
        self.last_bbox = bbox
        self.state = TrackingState.TRACKING
        return TrackingState.TRACKING, bbox

    def correct_target(self, dx, dy):       
        if self.state != TrackingState.TRACKING:
            return
        x = self.last_bbox[0] + dx
        y = self.last_bbox[1] + dy
        a = self.last_bbox[2]
        b = self.last_bbox[3]
        self.last_bbox = (x, y, a, b)
        self.start_tracking(self.last_frame, self.last_bbox)

    def resize_target(self, d_left, d_right, d_top, d_bottom):
        if self.state != TrackingState.TRACKING:
            return
        x = self.last_bbox[0] - d_left
        y = self.last_bbox[1] - d_top
        a = self.last_bbox[2] + d_left + d_right
        b = self.last_bbox[3] + d_top + d_bottom
        bbox = (x, y, a, b)
        if not self.__check_bbox(bbox):
            return
        self.last_bbox = bbox
        self.start_tracking(self.last_frame, self.last_bbox)
        
    def __create_tracker(self):
        # self.tracker = cv2.legacy.TrackerMOSSE_create()
        self.tracker = cv2.legacy.TrackerKCF_create()
        # self.tracker = cv2.legacy.TrackerCSRT_create()
        # self.tracker = cv2.legacy.TrackerBoosting_create()
        # self.tracker = cv2.legacy.TrackerMedianFlow_create()
        # self.tracker = cv2.legacy.TrackerTLD_create()
        # self.tracker = cv2.legacy.TrackerMIL_create()
        # self.tracker = cv2.legacy.TrackerGOTURN_create()

    def __check_bbox(self, bbox):
        return bbox[2] > self.minimal_roi_size and bbox[3] > self.minimal_roi_size