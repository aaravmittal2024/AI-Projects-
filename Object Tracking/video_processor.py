import cv2
from object_tracker import ObjectTracker

def process_video(video_path):
    """Process the video to detect and track moving objects."""
    
    # Initialize video stream and motion detector
    video_stream = cv2.VideoCapture(video_path)
    motion_detector = cv2.createBackgroundSubtractorMOG2(history=100, varThreshold=40)
    tracker = ObjectTracker()

    # Loop through video frames
    while video_stream.isOpened():
        success, current_frame = video_stream.read()
        if not success:
            break

        # Extract frame dimensions and region of interest
        frame_height, frame_width, _ = current_frame.shape
        region = extract_region_of_interest(current_frame, frame_height, frame_width)

        # Detect and track objects in the region
        detected_objects = detect_moving_objects(region, motion_detector)
        tracked_objects = tracker.track_objects(detected_objects)

        # Display the results
        display_results(region, current_frame, detected_objects, tracked_objects)

        # Break loop on 'Esc' key press
        if cv2.waitKey(30) == 27:
            break

    # Release resources after processing
    cleanup_resources(video_stream)

def extract_region_of_interest(frame, height, width):
    """Extract a specified region from the video frame."""
    return frame[340: 720, 500: 800]

def detect_moving_objects(region, detector):
    """Detect moving objects in the given region using the provided detector."""
    
    # Apply motion detector and threshold to get binary mask
    binary_mask = detector.apply(region)
    _, thresholded_mask = cv2.threshold(binary_mask, 254, 255, cv2.THRESH_BINARY)
    
    # Extract contours from the binary mask
    contours, _ = cv2.findContours(thresholded_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # Filter and return bounding rectangles of detected objects
    objects = [cv2.boundingRect(contour) for contour in contours if cv2.contourArea(contour) > 100]
    return objects

def display_results(region, frame, detected_objects, tracked_objects):
    """Display the region, full frame, and tracked objects."""
    
    # Draw tracked object IDs and bounding boxes on the region
    for box in tracked_objects:
        x, y, w, h, obj_id = box
        cv2.putText(region, str(obj_id), (x, y - 15), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)
        cv2.rectangle(region, (x, y), (x + w, y + h), (0, 255, 0), 3)

    # Show the processed region and original frame
    cv2.imshow("Region", region)
    cv2.imshow("Full Frame", frame)

def cleanup_resources(video_stream):
    """Release video stream and destroy all OpenCV windows."""
    video_stream.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    process_video("highway.mp4")
