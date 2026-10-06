import cv2
import os
from pathlib import Path

# Define paths
evidence_folder = r"c:\Users\Ved Jadhav\OneDrive\Desktop\women\evidence"
output_folder = r"c:\Users\Ved Jadhav\OneDrive\Desktop\women\evidence_png"

# Create output folder if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

# Get all AVI files
avi_files = sorted([f for f in os.listdir(evidence_folder) if f.endswith('.avi')])

print(f"Found {len(avi_files)} AVI files to process...")

# Process each AVI file
for idx, avi_file in enumerate(avi_files):
    video_path = os.path.join(evidence_folder, avi_file)
    print(f"\n[{idx+1}/{len(avi_files)}] Processing: {avi_file}")
    
    try:
        # Open video file
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            print(f"  ERROR: Could not open video file")
            continue
        
        frame_count = 0
        file_name = os.path.splitext(avi_file)[0]
        
        # Extract frames
        while True:
            ret, frame = cap.read()
            
            if not ret:
                break
            
            # Create output folder for this video
            video_output_folder = os.path.join(output_folder, file_name)
            os.makedirs(video_output_folder, exist_ok=True)
            
            # Save frame as PNG
            output_path = os.path.join(video_output_folder, f"frame_{frame_count:04d}.png")
            cv2.imwrite(output_path, frame)
            frame_count += 1
        
        cap.release()
        print(f"  Extracted {frame_count} frames")
        
    except Exception as e:
        print(f"  ERROR: {str(e)}")

print(f"\n✓ Processing complete! PNG files saved to: {output_folder}")
