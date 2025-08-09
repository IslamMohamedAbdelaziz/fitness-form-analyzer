# **Fitness Form Analysis API**

## **1\. Project Overview**

This project is a Flask-based REST API designed to analyze user-submitted exercise videos. It uses 2D pose estimation to identify squats and push-ups, count repetitions, and provide real-time form feedback. The service returns a detailed JSON response for programmatic use and is built to be a scalable and accurate tool for fitness applications.

The core of the service is an analysis engine that processes video frames to:

* Detect human pose landmarks using **MediaPipe**  
* Calculate joint angles to determine the state of an exercise.  
* Implement a Finite-State Machine (FSM) for robust repetition counting.  
* Assess the quality of each repetition based on a set of biomechanical rules.

## **2\. Setup and Installation**

You can run this project using either a standard Python virtual environment or Docker for containerization.

### **Option A: Virtual Environment Setup**

**Instructions:**

1. **Clone the repository:**  
   git clone \<repository-url\>  
   cd \<repository-name\>

2. **Create and activate a virtual environment:**  
   \# For Windows  
   python \-m venv venv  
   .\\venv\\Scripts\\activate

   \# For macOS/Linux  
   python3 \-m venv venv  
   source venv/bin/activate

3. **Install the required dependencies:**  
   pip install \-r requirements.txt

4. **Run the Flask application:**  

   \# python app.py

   The API will now be running at http://127.0.0.1:5000.

### **Option B: Docker Setup**

**Prerequisites:**

* Docker installed and running.

**Instructions:**

1. **Build the Docker image:**  
   docker build \-t fitness-analyzer .

2. **Run the Docker container:**  
   docker run \-p 5000:5000 fitness-analyzer

   The API will be accessible at http://127.0.0.1:5000.

## **3\. API Usage**

The API has a single endpoint for video analysis.

### **POST /analyze**

Accepts a multipart/form-data request containing a video file.

**Parameters:**

* video: The video file to be analyzed (e.g., .mp4).

**API usage examples with http:**
Run this command in the terminal 

http --form POST http://127.0.0.1:5000/analyze video@c:/Users/<username>/Downloads/PoseDetector/input_video/video_name.mp4

**Example Success Response (200 OK):**

{  
  "video\_id": "a-unique-uuid-string",  
  "summary": {  
    "squats": {  
      "total\_reps": 5,  
      "good\_form\_reps": 4,  
      "common\_issues": \["INSUFFICIENT\_DEPTH"\]  
    },  
    "pushups": {  
      "total\_reps": 10,  
      "good\_form\_reps": 8,  
      "common\_issues": \["BODY\_LINE\_BREAK"\]  
    }  
  },  
  "frame\_data": \[  
    {  
      "frame\_index": 50,  
      "exercise": "squat",  
      "rep\_id": 1,  
      "is\_form\_ok": true,  
      "angles": {  
        "knee": 75.4,  
        "elbow": 170.1  
      }  
    },  
    {  
      "frame\_index": 51,  
      "exercise": "squat",  
      "rep\_id": 1,  
      "is\_form\_ok": false,  
      "angles": {  
        "knee": 85.2,  
        "elbow": 169.5  
      }  
    }  
  \]  
}

## **4\. Technical Details & Limitations**

Model Choice
MediaPipe Pose: We chose Google's MediaPipe Pose framework for this project. 

Squats:

Repetition Counting: A rep is counted when the user moves from a standing state (knee_angle > 160°) to a squatting state (knee_angle < 90°).

 Insufficient Depth: Flagged if the horizontal position of the knee moves significantly forward past the ankle side-view perspective (left_knee[x] > left_ankle[x] + 40 pixels).

Push-ups:

Repetition Counting: A rep is counted when the user moves from an "up" state (elbow_angle > 160°) to a "down" state (elbow_angle < 90°).

Body Line Break: Flagged if the hips sag or pike significantly. This is checked by measuring the vertical distance between the hip and shoulder keypoints.

Known Limitations
2D Perspective: The analysis is based on 2D keypoints and is highly dependent on the camera angle. The model performs best with a clear side view of the user. Front-facing or angled videos will produce inaccurate results.

Single Person Only: The current logic is designed to track only one person in the frame.

Hardcoded Thresholds: Form-checking rules (e.g., the 40 pixel offset for knee travel) are based on hardcoded pixel values and may not be accurate for all video resolutions or user distances from the camera. A more robust solution would use ratios of body parts.

No Keypoint Smoothing: The provided code does not yet implement a temporal filter. This can lead to jitter in the angle calculations.
