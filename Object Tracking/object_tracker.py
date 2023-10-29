import math

class ObjectTracker:
    """Class to track objects based on their Euclidean distance between frames."""
    
    def __init__(self):
        self._object_centers = {}
        self._next_id = 0

    def track_objects(self, object_rectangles):
        """Track objects and return their bounding rectangles with associated IDs."""
        
        tracked_objects = []
        for rect in object_rectangles:
            center_x, center_y = self._calculate_center(rect)
            matched_id = self._find_matching_id(center_x, center_y)

            if matched_id is None:
                matched_id = self._next_id
                self._object_centers[matched_id] = (center_x, center_y)
                self._next_id += 1

            tracked_objects.append((*rect, matched_id))

        self._cleanup_unused_ids(tracked_objects)
        return tracked_objects

    def _calculate_center(self, rectangle):
        """Calculate and return the center of a given rectangle."""
        
        x, y, w, h = rectangle
        return (x + w // 2, y + h // 2)

    def _find_matching_id(self, x, y):
        """Find and return the ID of an object that matches the given center coordinates."""
        
        for obj_id, (center_x, center_y) in self._object_centers.items():
            distance = math.hypot(x - center_x, y - center_y)
            if distance < 25:
                self._object_centers[obj_id] = (x, y)
                return obj_id
        return None

    def _cleanup_unused_ids(self, tracked_objects):
        """Remove IDs that are no longer in use."""
        
        active_ids = {obj[-1] for obj in tracked_objects}
        self._object_centers = {k: v for k, v in self._object_centers.items() if k in active_ids}
