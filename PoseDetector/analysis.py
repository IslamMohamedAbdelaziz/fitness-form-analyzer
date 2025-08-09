import numpy as np
import os
import csv
import json
from pose_detector import PoseDetector # type: ignore
# ----------------- EMA FILTER -----------------
previous_smoothed_landmarks = None

def smooth_landmarks(landmarks, alpha=0.2):
    """
    Apply EMA smoothing to reduce jitter in keypoint positions.
    """
    global previous_smoothed_landmarks
    if landmarks is None or len(landmarks) == 0:
        return landmarks

    if previous_smoothed_landmarks is None:
        previous_smoothed_landmarks = landmarks
        return landmarks

    smoothed = []
    for prev, curr in zip(previous_smoothed_landmarks, landmarks):
        lm_id = curr[0]
        sm_x = alpha * curr[1] + (1 - alpha) * prev[1]
        sm_y = alpha * curr[2] + (1 - alpha) * prev[2]
        smoothed.append([lm_id, sm_x, sm_y])

    previous_smoothed_landmarks = smoothed
    return smoothed
# ------------------------------------------------

def calculate_angle(a, b, c):
    """
    Calculates the angle between three points.
    """
    a = np.array(a)  # First
    b = np.array(b)  # Mid
    c = np.array(c)  # End

    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - \
              np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)

    if angle > 180.0:
        angle = 360 - angle

    return angle

def analyze_video(frames,video_id):
    """
    Analyzes a list of video frames for squats and push-ups.
    """
    detector = PoseDetector()
    squat_counter = 0
    pushup_counter = 0
    squat_stage = None
    pushup_stage = None
    squat_form_issues = []
    pushup_form_issues = []
    frame_data = []

    for idx, frame in enumerate(frames):
        frame = detector.find_pose(frame, draw=False)
        landmarks = detector.get_landmarks(frame)
        # 🔹 Apply EMA temporal smoothing
        landmarks = smooth_landmarks(landmarks, alpha=0.2)
        is_form_ok_this_frame = True
        if not landmarks:
            continue

        # Squat analysis
        left_hip = landmarks[23][1:]
        left_knee = landmarks[25][1:]
        left_ankle = landmarks[27][1:]
        knee_angle = calculate_angle(left_hip, left_knee, left_ankle)

        if knee_angle > 160:
            squat_stage = "up"
        if knee_angle < 90 and squat_stage == 'up':
            squat_stage = "down"
            squat_counter += 1
            # Form check
            if abs(left_knee[0] - left_ankle[0]) > 40: # Simplified check
                squat_form_issues.append("INSUFFICIENT_DEPTH")
                is_form_ok_this_frame = False

        # Push-up analysis
        left_shoulder = landmarks[11][1:]
        left_elbow = landmarks[13][1:]
        left_wrist = landmarks[15][1:]
        elbow_angle = calculate_angle(left_shoulder, left_elbow, left_wrist)

        if elbow_angle > 160:
            pushup_stage = "up"
        if elbow_angle < 90 and pushup_stage == 'up':
            pushup_stage = "down"
            pushup_counter += 1
            # Form check
            hip_shoulder_ankle_alignment = abs(left_hip[1] - left_shoulder[1])
            if hip_shoulder_ankle_alignment > 40: # Simplified check
                pushup_form_issues.append("BODY_LINE_BREAK")
                is_form_ok_this_frame = False
         # save frame data
        frame_data.append({
            "frame_index": idx,
            "exercise": "squat" if knee_angle < 160 else "pushup" if elbow_angle < 160 else "none",
            "rep_id": squat_counter if knee_angle < 160 else pushup_counter if elbow_angle < 160 else 0,
            "is_form_ok": is_form_ok_this_frame,
            "angles": {"knee": knee_angle, "elbow": elbow_angle}
        })

    # save the analysis summary
    analysis_summary = {
            "squats": {
                "total_reps": squat_counter,
                "good_form_reps": squat_counter - len(set(squat_form_issues)),
                "common_issues": list(set(squat_form_issues))
            },
            "pushups": {
                "total_reps": pushup_counter,
                "good_form_reps": pushup_counter - len(set(pushup_form_issues)),
                "common_issues": list(set(pushup_form_issues))
            }
        }
    
    summary_video_id = {"video_id": video_id,
        "summary": analysis_summary,}

    # Create output directory
    output_dir = " report/"
    os.makedirs(output_dir, exist_ok=True)

    # 1️⃣ Save frame-by-frame data to CSV
    csv_path = os.path.join(output_dir, "result.csv")
    with open(csv_path, mode='w', newline='') as csv_file:
        if frame_data:
            writer = csv.DictWriter(csv_file, fieldnames= frame_data[0].keys())
            writer.writeheader()
            writer.writerows(frame_data)

    # 2️⃣ Save summary block to JSON
    summary_path = os.path.join(output_dir, "summary.json")
    with open(summary_path, 'w') as json_file:
        json.dump(summary_video_id, json_file, indent=4)

    return {
        "video_id": video_id,
        "summary": analysis_summary,
        "frame_data": frame_data
    }
