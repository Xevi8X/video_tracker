#ifndef VIDEO_TRACKER_H
#define VIDEO_TRACKER_H

#include <opencv2/opencv.hpp>
#include <opencv2/tracking.hpp>

enum class TrackingState {
    UNINITIALIZED,
    TRACKING,
    SEARCHING,
    TARGET_LOST
};

class VideoTracker {
public:
    VideoTracker(cv::Size frame_size);
    cv::Rect startTracking(cv::Mat& frame, cv::Rect& bbox);
    std::pair<TrackingState, cv::Rect> updateTracking(cv::Mat& frame);
    void correctTarget(int dx, int dy);
    void resizeTarget(int d_left, int d_right, int d_top, int d_bottom);

private:
    void createTracker();
    bool checkBbox(const cv::Rect& bbox);

    cv::Size frame_size_;
    cv::Ptr<cv::Tracker> tracker_;
    cv::VideoCapture cap_;
    cv::Rect bbox_;
    TrackingState state_;
    cv::Mat last_frame_;
    int searching_counter_;
    int search_frame_limit_;
    int minimal_roi_size_;
};

#endif // VIDEO_TRACKER_H
