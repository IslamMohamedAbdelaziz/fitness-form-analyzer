import cv2
import mediapipe as mp

class PoseDetector:
    """
    A class to detect pose landmarks from an image.
    """
    def __init__(self, static_image_mode=False, model_complexity=1, smooth_landmarks=True,
                 enable_segmentation=False, smooth_segmentation=True,
                 min_detection_confidence=0.5, min_tracking_confidence=0.5):
        self.static_image_mode = static_image_mode
        self.model_complexity = model_complexity
        self.smooth_landmarks = smooth_landmarks
        self.enable_segmentation = enable_segmentation
        self.smooth_segmentation = smooth_segmentation
        self.min_detection_confidence = min_detection_confidence
        self.min_tracking_confidence = min_tracking_confidence

        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(self.static_image_mode, self.model_complexity,
                                      self.smooth_landmarks, self.enable_segmentation,
                                      self.smooth_segmentation, self.min_detection_confidence,
                                      self.min_tracking_confidence)
        self.mp_draw = mp.solutions.drawing_utils

    def find_pose(self, img, draw=True):
        """
        Finds pose landmarks in an image.
        """
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.pose.process(img_rgb)
        if self.results.pose_landmarks and draw:
            self.mp_draw.draw_landmarks(img, self.results.pose_landmarks,
                                        self.mp_pose.POSE_CONNECTIONS)
        return img

    def get_landmarks(self, img):
        """
        Extracts pose landmarks from the image.
        """
        landmarks = []
        if self.results.pose_landmarks:
            for lm_id, lm in enumerate(self.results.pose_landmarks.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                landmarks.append([lm_id, cx, cy])
        return landmarks

