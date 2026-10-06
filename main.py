import cv2
import time
import numpy as np
import threading
import smtplib
import datetime
import os
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders

from flask import Flask, render_template, Response, jsonify

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("[ERROR] Pillow is not installed. Run 'pip install pillow'.")
    import sys
    sys.exit(1)

app = Flask(__name__)

# --- GLOBAL DATA FOR WEB DASHBOARD ---
global_frame = None
global_logs = []

def add_log(msg):
    t = datetime.datetime.now().strftime('%H:%M:%S')
    global_logs.insert(0, {"time": t, "msg": msg})
    if len(global_logs) > 30:
        global_logs.pop()

# --- CONFIGURATION (PERCENTAGE BASED) ---
NOISE_MOTION_PERCENT = 0.005      
AGGRESSIVE_MOTION_PERCENT = 0.06 
EXPOSURE_SPIKE_PERCENT = 0.90    
COOLDOWN_TIME = 3                

# --- EMAIL CONFIGURATION ---
SENDER_EMAIL = "vedjadhav55@gmail.com"
APP_PASSWORD = "whyr byzu wult qhdc" 
RECEIVER_EMAIL = "jadhavved17@gmail.com"

def init_gender_detector():
    try:
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        if face_cascade.empty():
            add_log("WARNING ⚠️ Haarcascade not loaded. Face detection disabled.")
            return None, None   
        genderNet = cv2.dnn.readNet("gender_net.caffemodel", "gender_deploy.prototxt")
        return face_cascade, genderNet
    except Exception as e:
        add_log(f"WARNING ⚠️ Gender model not found. Running without gender detection.")
        try:
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
            if not face_cascade.empty():
                return face_cascade, None
        except:
            pass
        return None, None

def get_real_location():
    try:
        import json
        import urllib.request
        # 3 second timeout so the system doesn't freeze if internet is slow
        with urllib.request.urlopen("http://ip-api.com/json/", timeout=3) as response:
            data = json.loads(response.read().decode())
            return f"{data.get('city', 'Unknown')}, {data.get('regionName', 'Unknown')}, {data.get('country', 'Unknown')} (Lat: {data.get('lat')}, Lon: {data.get('lon')})"
    except:
        return "Location Unavailable (Network/GPS Offline)"

def send_alert_email(video_path):
    add_log(f"Preparing to send secure email with evidence: {os.path.basename(video_path)}")
    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = RECEIVER_EMAIL
        msg['Subject'] = "URGENT [SHESECURE]: Suspicious Activity Detected on Camera!"
        
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        real_location = get_real_location()
        
        body = f"""
        <html>
            <body>
                <h2 style="color:red;">SHESECURE AI - THREAT ALERT</h2>
                <p><b>Timestamp:</b> {timestamp}</p>
                <p><b>Live GPS Location:</b> {real_location} (Camera ID: SHESECURE-01)</p>
                <p><b>Threat Level:</b> HIGH - Aggressive Physical Force Detected</p>
                <p><b>Additional Data:</b> The AI kinematic tracking system has isolated the exact timeframe of the aggressive action. Attached is the encrypted .mp4 video evidence of the incident for immediate review by authorities.</p>
                <br>
                <p><i>Generated automatically by SHESECURE Security Engine</i></p>
            </body>
        </html>
        """
        msg.attach(MIMEText(body, 'html'))

        if os.path.exists(video_path):
            with open(video_path, "rb") as attachment:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", f"attachment; filename= {os.path.basename(video_path)}")
            msg.attach(part)

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SENDER_EMAIL, APP_PASSWORD)
        server.send_message(msg)
        server.quit()
        add_log(f"SUCCESS ✓ Email alert & video delivered to {RECEIVER_EMAIL}!")
    except Exception as e:
        add_log(f"ERROR ❌ Email failed: {str(e)[:60]}")

def draw_futuristic_box(img, x, y, w, h, color, thickness=2, length=15):
    cv2.line(img, (x, y), (x + length, y), color, thickness)
    cv2.line(img, (x, y), (x, y + length), color, thickness)
    cv2.line(img, (x + w, y), (x + w - length, y), color, thickness)
    cv2.line(img, (x + w, y), (x + w, y + length), color, thickness)
    cv2.line(img, (x, y + h), (x + length, y + h), color, thickness)
    cv2.line(img, (x, y + h), (x, y + h - length), color, thickness)
    cv2.line(img, (x + w, y + h), (x + w - length, y + h), color, thickness)
    cv2.line(img, (x + w, y + h), (x + w, y + h - length), color, thickness)

def get_font(name, size):
    try:
        return ImageFont.truetype(name, size)
    except:
        try:
            return ImageFont.truetype("arial.ttf", size)
        except:
            return ImageFont.load_default()

# --- THE NATIVE AI LOOP ---
def run_ai_logic():
    global global_frame
    
    add_log("SYSTEM BOOTING: Connecting to Live Camera feed...")
    
    face_cascade, genderNet = init_gender_detector()
    if face_cascade:
        add_log("Deep Learning Neural Networks successfully loaded.")
        
    GENDER_LIST = ['Male', 'Female']
    MODEL_MEAN_VALUES = (78.4263377603, 87.7689143744, 114.895847746)
    
    font_large = get_font("segoeuib.ttf", 26)  
    font_main = get_font("segoeui.ttf", 18)    
    font_data = get_font("consola.ttf", 14)    
    
    try:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            add_log("ERROR ❌ Camera not available. System running in monitoring mode.")
            return
        time.sleep(2) 
        add_log("Camera Online. Motion Tracker is Armed.")
    except Exception as e:
        add_log(f"ERROR ❌ Camera initialization failed: {str(e)[:50]}")
        return
    
    import mediapipe.python.solutions.drawing_utils as mp_drawing
    import mediapipe.python.solutions.pose as mp_pose
    import mediapipe.python.solutions.drawing_styles as mp_drawing_styles
    pose_tracker = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

    try:
        import pickle
        with open("models/action_model.pkl", "rb") as f:
            action_model = pickle.load(f)
        add_log("Custom Neural Skeletal Model LOADED.")
    except Exception as e:
        add_log("ERROR \u274c Custom action_model.pkl not found! Please run collect_data.py and train_model.py first!")
        return
    
    status = "Normal"
    color = (0, 255, 0) 
    last_suspicious_time = 0
    recording = False
    out = None
    video_filename = ""
    start_time = time.time()
    warmup_duration = 4.0 
    
    if not os.path.exists("evidence"):
        os.makedirs("evidence")
        add_log("Created secure local /evidence repository.")
    
    while True:
        ret, frame = cap.read()
        if not ret: 
            add_log("ERROR \u274c Camera feed lost!")
            break
        
        frame = cv2.flip(frame, 1)
        height, width, _ = frame.shape
        total_frame_area = height * width
        
        MOTION_THRESHOLD = total_frame_area * NOISE_MOTION_PERCENT
        AGGRESSIVE_MOTION_THRESHOLD = total_frame_area * AGGRESSIVE_MOTION_PERCENT
        
        if out is None and recording:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            video_filename = f"evidence/alert_{int(time.time())}.mp4"
            out = cv2.VideoWriter(video_filename, fourcc, 10.0, (width, height))
            
        if recording and out is not None:
            out.write(frame)
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        pil_labels = []

        # -----------------------------
        #  GENDER TARGETING (Caffe Model)
        # -----------------------------
        if face_cascade is not None and genderNet is not None:
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5, minSize=(60, 60))
            for (x, y, w, h) in faces:
                padding = 20
                y1, y2 = max(0, y - padding), min(frame.shape[0]-1, y + h + padding)
                x1, x2 = max(0, x - padding), min(frame.shape[1]-1, x + w + padding)
                face_crop = frame[y1:y2, x1:x2]
                
                if face_crop.shape[0] > 0 and face_crop.shape[1] > 0:
                    blob = cv2.dnn.blobFromImage(face_crop, 1.0, (227, 227), MODEL_MEAN_VALUES, swapRB=False)
                    genderNet.setInput(blob)
                    preds = genderNet.forward()
                    
                    gender = GENDER_LIST[preds[0].argmax()]
                    conf = preds[0].max() * 100
                    
                    box_color = (200, 100, 255) if gender == 'Female' else (255, 200, 50)
                    draw_futuristic_box(frame, x, y, w, h, box_color, thickness=2, length=20)
                    
                    cx, cy = x + w//2, y + h//2
                    cv2.line(frame, (cx - 5, cy), (cx + 5, cy), box_color, 1)
                    cv2.line(frame, (cx, cy - 5), (cx, cy + 5), box_color, 1)
                    
                    pil_labels.append({
                        "text": f"{gender.upper()} [{conf:.1f}%]",
                        "pos": (x, y - 25),
                        "color": box_color,
                        "font": font_main
                    })
                    
        # -----------------------------
        #  CUSTOM SKELETAL AI PREDICTION
        # -----------------------------
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose_tracker.process(image_rgb)
        
        current_prediction = "Normal"
        threat_confidence = 0.0
        
        if results.pose_landmarks:
            mp_drawing.draw_landmarks(
                frame, 
                results.pose_landmarks, 
                mp_pose.POSE_CONNECTIONS,
                mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                mp_drawing.DrawingSpec(color=(0, 255, 255), thickness=2, circle_radius=2)
            )
            
            # Extract the exact same robust mathematical features used in training
            landmarks = results.pose_landmarks
            nose = landmarks.landmark[mp_pose.PoseLandmark.NOSE]
            left_shoulder = landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER]
            left_hip = landmarks.landmark[mp_pose.PoseLandmark.LEFT_HIP]
            
            import math
            torso_length = math.hypot(left_shoulder.x - left_hip.x, left_shoulder.y - left_hip.y)
            if torso_length < 0.001: torso_length = 0.001
                
            row = []
            for lm in landmarks.landmark:
                norm_x = lm.x - nose.x
                norm_y = lm.y - nose.y
                norm_z = lm.z - nose.z
                row.extend([norm_x / torso_length, norm_y / torso_length, norm_z / torso_length, lm.visibility])
            
            # Predict the action using our custom trained model
            prediction_array = action_model.predict_proba([row])[0]
            
            # Our classes are sorted alphabetically by scikit-learn ['Aggressive', 'Normal']
            class_labels = action_model.classes_
            predicted_class_index = np.argmax(prediction_array)
            current_prediction = class_labels[predicted_class_index]
            
            if "Aggressive" in class_labels:
                agg_index = list(class_labels).index("Aggressive")
                threat_confidence = prediction_array[agg_index] * 100
            
        time_elapsed = time.time() - start_time
        if time_elapsed < warmup_duration:
            status = "SYSTEM CALIBRATION"
            color = (255, 255, 0)
        else:
            if current_prediction == "Aggressive":
                if "THREAT" not in status:
                    status = "THREAT DETECTED"
                    color = (0, 0, 255) 
                last_suspicious_time = time.time()
            elif current_prediction == "Normal" and results.pose_landmarks:
                if time.time() - last_suspicious_time > COOLDOWN_TIME:
                    status = "SUBJECT IN MOTION"
                    color = (0, 200, 255) 
            else:
                if time.time() - last_suspicious_time > COOLDOWN_TIME:
                    status = "SECURE (STATIC)"
                    color = (0, 255, 0)
                    
        if "THREAT" in status and not recording:
            add_log("THREAT PROTOCOL ENGAGED: Suspicious force detected! Recording locally to /evidence...")
            recording = True
                
        elif "THREAT" not in status and recording and (time.time() - last_suspicious_time > COOLDOWN_TIME):
            add_log("Activity normalized. Securing video evidence & dispatching Email alerts...")
            recording = False
            if out is not None:
                out.release()
                out = None
                
            threading.Thread(target=send_alert_email, args=(video_filename,), daemon=True).start()
            
        # -----------------------------
        #  OPENCV HUD OVERLAYS (Boxes/Lines)
        # -----------------------------
        hud_overlay = frame.copy()
        cv2.rectangle(hud_overlay, (0, 0), (width, 85), (8, 10, 15), -1) 
        cv2.rectangle(hud_overlay, (0, height - 35), (width, height), (8, 10, 15), -1)
        cv2.addWeighted(hud_overlay, 0.90, frame, 0.10, 0, frame)
        
        cv2.line(frame, (0, 85), (width, 85), (150, 150, 150), 1)
        cv2.line(frame, (0, height - 35), (width, height - 35), (150, 150, 150), 1)
        
        if recording and int(time.time() * 2) % 2 == 0:
            cv2.circle(frame, (width - 165, 42), 6, (0, 0, 255), -1)

        # -----------------------------
        #  PIL TRUE-TYPE FONT RENDERING
        # -----------------------------
        pil_img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(pil_img)

        def render_text(text, coords, src_color, font, shadow_offset=2):
            r, g, b = src_color[2], src_color[1], src_color[0]
            draw.text((coords[0]+shadow_offset, coords[1]+shadow_offset), text, font=font, fill=(0, 0, 0, 180))
            draw.text(coords, text, font=font, fill=(r, g, b, 255))

        render_text(f"STATUS: {status}", (20, 15), color, font_large)
        
        if "CALIBRATION" in status:
            render_text("Adjusting ISO and Lens Parameters...", (22, 55), (200, 200, 200), font_main)
        else:
            confidence_score = min(99.9, (current_motion_area / AGGRESSIVE_MOTION_THRESHOLD) * 100)
            if "THREAT" in status:
                render_text(f"CONFIDENCE: {confidence_score:.1f}%", (20, 55), (0, 0, 255), font_main)
            else:
                render_text(f"MOTION INDEX: {int(current_motion_area)}", (22, 55), (200, 200, 200), font_main)

        if recording:
            render_text("REC [CLOUD SYNC]", (width - 150, 30), (0, 0, 255), font_main)

        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        render_text(f"SYS::TIME [{timestamp}]  //  CORE::SHESECURE_AI_MONITOR", (20, height - 28), (0, 255, 255), font_data)
        render_text("FPS: 30", (width - 70, height - 28), (0, 255, 0), font_data)

        for lbl in pil_labels:
            render_text(lbl["text"], lbl["pos"], lbl["color"], lbl["font"], shadow_offset=1)

        frame = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
        
        global_frame = frame.copy()
        
        cv2.imshow('SHESECURE AI Target Module - SERVER RUNNING', frame)
        if cv2.waitKey(1) & 0xFF in [ord('q'), ord('Q'), 27]:
            break

    if out is not None:
        out.release()
    cap.release()
    cv2.destroyAllWindows()
    os._exit(0)

# --- FLASK WEB SERVER ROUTES ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/logs')
def get_logs():
    return jsonify(global_logs)

def generate_web_feed():
    global global_frame
    while True:
        if global_frame is not None:
            ret, buffer = cv2.imencode('.jpg', global_frame)
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        else:
            time.sleep(0.1)
        time.sleep(0.04)

@app.route('/video_feed')
def video_feed():
    return Response(generate_web_feed(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    print("\n" + "="*50)
    print("     STARTING SHESECURE DASHBOARD ENGINE")
    print("="*50)
    
    threading.Thread(target=run_ai_logic, daemon=True).start()
    
    print("\n\n---> Please open your web browser to: http://127.0.0.1:5000\n\n")
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)