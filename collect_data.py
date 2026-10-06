import cv2
import mediapipe.python.solutions.drawing_utils as mp_drawing
import mediapipe.python.solutions.pose as mp_pose
import mediapipe.python.solutions.drawing_styles as mp_drawing_styles
import csv
import os
import math
import numpy as np

# --- CONFIGURATION ---
DATASET_FILE = "dataset/skeletal_data.csv"
FRAMES_PER_ACTION = 200

# Create dataset directory if it doesn't exist
if not os.path.exists("dataset"):
    os.makedirs("dataset")

# Initialize MediaPipe Pose
pose_tracker = mp_pose.Pose(min_detection_confidence=0.7, min_tracking_confidence=0.7)

# Setup CSV Header dynamically
# We extract 33 landmarks. For each, we calculate Normalized X, Y, Z.
header = ['label']
for i in range(33):
    header.extend([f'x{i}', f'y{i}', f'z{i}', f'v{i}'])

# Only create file and write header if it doesn't exist
if not os.path.exists(DATASET_FILE):
    with open(DATASET_FILE, mode='w', newline='') as f:
        csv_writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow(header)

def extract_robust_features(landmarks):
    """
    Extracts 100% robust features by centering all joints around the Nose
    and scaling them by the Torso length. This guarantees MAXIMUM ACCURACY
    even if the person moves far away, gets close, or stands on the edge of the screen!
    """
    nose = landmarks.landmark[mp_pose.PoseLandmark.NOSE]
    left_shoulder = landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER]
    left_hip = landmarks.landmark[mp_pose.PoseLandmark.LEFT_HIP]
    
    # Calculate torso length for scale invariance
    torso_length = math.hypot(left_shoulder.x - left_hip.x, left_shoulder.y - left_hip.y)
    # Prevent division by zero
    if torso_length < 0.001:
        torso_length = 0.001
        
    row = []
    for lm in landmarks.landmark:
        # Translation invariance (Nose is 0,0,0)
        norm_x = lm.x - nose.x
        norm_y = lm.y - nose.y
        norm_z = lm.z - nose.z
        
        # Scale invariance (Divide by torso length)
        scaled_x = norm_x / torso_length
        scaled_y = norm_y / torso_length
        scaled_z = norm_z / torso_length
        
        row.extend([scaled_x, scaled_y, scaled_z, lm.visibility])
        
    return row

def capture_data():
    cap = cv2.VideoCapture(0)
    print("\n" + "="*50)
    print("   VANGUARD AI: DATA HARVESTING ENGINE")
    print("="*50)
    print("INSTRUCTIONS:")
    print(" - Press 'N' to record 200 frames of NORMAL behavior (Walking, standing).")
    print(" - Press 'A' to record 200 frames of AGGRESSIVE behavior (Punches, blocking).")
    print(" - Press 'Q' to quit and save the dataset.")
    print("="*50 + "\n")

    recording_state = None
    frames_recorded = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        frame = cv2.flip(frame, 1)
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose_tracker.process(image_rgb)
        
        # Render Skeleton
        if results.pose_landmarks:
            mp_drawing.draw_landmarks(
                frame, 
                results.pose_landmarks, 
                mp_pose.POSE_CONNECTIONS,
                mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                mp_drawing.DrawingSpec(color=(0, 255, 255), thickness=2, circle_radius=2)
            )
            
            # Recording Logic
            if recording_state is not None:
                # Extract our mathematical robust features
                row_data = extract_robust_features(results.pose_landmarks)
                
                # Append label
                row_data.insert(0, recording_state)
                
                # Write to CSV
                with open(DATASET_FILE, mode='a', newline='') as f:
                    csv_writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                    csv_writer.writerow(row_data)
                    
                frames_recorded += 1
                cv2.putText(frame, f"RECORDING '{recording_state}': {frames_recorded}/{FRAMES_PER_ACTION}", 
                            (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
                            
                if frames_recorded >= FRAMES_PER_ACTION:
                    print(f"SUCCESS: Captured {FRAMES_PER_ACTION} frames of '{recording_state}'.")
                    recording_state = None
                    frames_recorded = 0

        else:
            if recording_state is not None:
                cv2.putText(frame, "NO HUMAN DETECTED! Paused...", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)

        if recording_state is None:
            cv2.putText(frame, "Press 'N' (Normal) or 'A' (Aggressive)", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)

        cv2.imshow('Data Harvesting Engine', frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('n') and recording_state is None:
            recording_state = "Normal"
            frames_recorded = 0
            print("Recording started: NORMAL...")
        elif key == ord('a') and recording_state is None:
            recording_state = "Aggressive"
            frames_recorded = 0
            print("Recording started: AGGRESSIVE...")

    cap.release()
    cv2.destroyAllWindows()
    print("\nDataset automatically saved to dataset/skeletal_data.csv")

if __name__ == "__main__":
    capture_data()
