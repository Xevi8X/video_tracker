#include <opencv2/opencv.hpp>
#include "video_tracker.h"
#include <iostream>
#include <chrono>

cv::Point click_pos(-1, -1);

void mouseEvent(int event, int x, int y, int flags, void* userdata) {
    if (event == cv::EVENT_LBUTTONDOWN) {
        click_pos = cv::Point(x, y);
    }
}

int main() {
    cv::VideoCapture cap("rtsp://localhost:8554/example");
    if (!cap.isOpened()) {
        std::cerr << "Could not open webcam" << std::endl;
        return -1;
    }

    cv::Mat frame;
    for (int i = 0; i < 5; ++i) {
        if (!cap.read(frame)) {
            std::cerr << "Failed to read" << std::endl;
            cap.release();
            return -1;
        }
    }

    cv::Size frame_size(static_cast<int>(cap.get(cv::CAP_PROP_FRAME_WIDTH)),
                        static_cast<int>(cap.get(cv::CAP_PROP_FRAME_HEIGHT)));
    std::cout << "Frame size: " << frame_size.width << "x" << frame_size.height << std::endl;

    VideoTracker tracker(frame_size);
    cv::Mat last_frame;
    double fps = 0.0;
    int a = 40, correction_diff = 5, resize_diff = 5;
    auto last_time = std::chrono::steady_clock::now();

    cv::namedWindow("Tracking", cv::WINDOW_FULLSCREEN);
    cv::setMouseCallback("Tracking", mouseEvent);

    while (cap.isOpened()) {
        if (click_pos.x != -1 && !last_frame.empty()) {
            int x = std::clamp(click_pos.x, a, frame_size.width - a);
            int y = std::clamp(click_pos.y, a, frame_size.height - a);
            cv::Rect bbox(x - a, y - a, 2 * a, 2 * a);
            tracker.startTracking(last_frame, bbox);
            click_pos = cv::Point(-1, -1);
        }

        int key = cv::waitKey(1) & 0xFF;
        if (key == 27) {
            break;
        } else if (key == 'q') {
            tracker.resizeTarget(-resize_diff, -resize_diff, -resize_diff, -resize_diff);
        } else if (key == 'e') {
            tracker.resizeTarget(resize_diff, resize_diff, resize_diff, resize_diff);
        } else if (key == 'a' || key == 81) {
            tracker.correctTarget(-correction_diff, 0);
        } else if (key == 'w' || key == 82) {
            tracker.correctTarget(0, -correction_diff);
        } else if (key == 'd' || key == 83) {
            tracker.correctTarget(correction_diff, 0);
        } else if (key == 's' || key == 84) {
            tracker.correctTarget(0, correction_diff);
        }

        if (!cap.read(frame)) {
            break;
        }
        last_frame = frame.clone();

        auto [state, bbox] = tracker.updateTracking(frame);
        cv::Scalar color;
        if (state == TrackingState::TRACKING) {
            color = cv::Scalar(0, 255, 0);
        } else if (state == TrackingState::SEARCHING) {
            color = cv::Scalar(0, 255, 255);
        } else {
            color = cv::Scalar(0, 0, 0);
        }

        if (color != cv::Scalar(0, 0, 0)) {
            cv::rectangle(frame, bbox, color, 2, 1);
        }

        auto now = std::chrono::steady_clock::now();
        double fps_raw = 1.0 / std::chrono::duration_cast<std::chrono::duration<double>>(now - last_time).count();
        last_time = now;
        fps = 0.9 * fps + 0.1 * fps_raw;
        cv::putText(frame, std::to_string(static_cast<int>(fps)), cv::Point(10, 30),
                    cv::FONT_HERSHEY_SIMPLEX, 1, cv::Scalar(0, 255, 0), 2, cv::LINE_AA);

        cv::imshow("Tracking", frame);
    }

    cap.release();
    cv::destroyAllWindows();

    return 0;
}
