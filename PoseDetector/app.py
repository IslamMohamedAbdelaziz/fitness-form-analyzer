from flask import Flask, request, jsonify
import tempfile
import cv2
import os
import json
from analysis import analyze_video # type: ignore

app = Flask(__name__)

@app.route('/analyze', methods=['POST'])
def analyze():
    # Check if video is included in the request
    if 'video' not in request.files:
        return jsonify({'error': 'No video file provided'}), 400

    video = request.files['video']

    # Check if a file was selected
    if video.filename == '':
        return jsonify({'error': 'No video file selected'}), 400

    # Use a temp file to store the uploaded video
    with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_file:
        video.save(temp_file)
        temp_filename = temp_file.name

    try:
        # Open the video file with OpenCV
        cap = cv2.VideoCapture(temp_filename)

        if not cap.isOpened():
            return jsonify({'error': 'Could not open video file'}), 400

        # Read all frames
        frames = []
        while True:
            success, frame = cap.read()
            if not success:
                break
            frames.append(frame)

        cap.release()

        if not frames:
            return jsonify({'error': 'No frames were read from the video'}), 400

        print(f"Read {len(frames)} frames from the video. Starting analysis...")

        # Call your custom video analysis function
        analysis_results = analyze_video(frames, video.filename)

        print("\n--- Analysis Complete ---")
        print(json.dumps(analysis_results, indent=4))
        print("-----------------------\n")

        return jsonify(analysis_results)

    finally:
        # Always remove the temporary file
        if os.path.exists(temp_filename):
            os.remove(temp_filename)

if __name__ == '__main__':
    # Run the app.
    app.run( host='0.0.0.0', port=5000)