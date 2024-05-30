#include "video_tracker.h"

VideoTracker::VideoTracker(cv::Size frame_size)
    : frame_size_(frame_size), state_(TrackingState::UNINITIALIZED),
      search_frame_limit_(60), minimal_roi_size_(50), searching_counter_(0) {
    createTracker();
    cap_.open(0);
}

cv::Rect VideoTracker::startTracking(cv::Mat& frame, cv::Rect& bbox) {
    searching_counter_ = 0;
    bbox_ = bbox;
    createTracker();
    tracker_->init(frame, bbox);
    state_ = TrackingState::TRACKING;
    return bbox_;
}

std::pair<TrackingState, cv::Rect> VideoTracker::updateTracking(cv::Mat& frame) {
    if (state_ == TrackingState::UNINITIALIZED) {
        return { TrackingState::UNINITIALIZED, cv::Rect() };
    }

    last_frame_ = frame.clone();
    bool result = tracker_->update(frame, bbox_);
    if (!result || !checkBbox(bbox_)) {
        searching_counter_++;
        if (searching_counter_ > search_frame_limit_) {
            state_ = TrackingState::UNINITIALIZED;
            return { TrackingState::TARGET_LOST, cv::Rect() };
        }
        state_ = TrackingState::SEARCHING;
        return { TrackingState::SEARCHING, bbox_ };
    }

    searching_counter_ = 0;
    state_ = TrackingState::TRACKING;
    return { TrackingState::TRACKING, bbox_ };
}

void VideoTracker::correctTarget(int dx, int dy) {
    if (state_ != TrackingState::TRACKING) {
        return;
    }
    bbox_.x += dx;
    bbox_.y += dy;
    startTracking(last_frame_, bbox_);
}

void VideoTracker::resizeTarget(int d_left, int d_right, int d_top, int d_bottom) {
    if (state_ != TrackingState::TRACKING) {
        return;
    }
    bbox_.x -= d_left;
    bbox_.y -= d_top;
    bbox_.width += d_left + d_right;
    bbox_.height += d_top + d_bottom;
    if (!checkBbox(bbox_)) {
        return;
    }
    startTracking(last_frame_, bbox_);
}

void VideoTracker::createTracker() {
    tracker_ = cv::TrackerKCF::create();
}

bool VideoTracker::checkBbox(const cv::Rect& bbox) {
    return bbox.x >= 0 && bbox.y >= 0 && bbox.x + bbox.width <= frame_size_.width &&
           bbox.y + bbox.height <= frame_size_.height && bbox.width > minimal_roi_size_ &&
           bbox.height > minimal_roi_size_;
}
