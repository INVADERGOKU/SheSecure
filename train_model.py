import pandas as pd
import numpy as np
import os
import pickle
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

# --- CONFIGURATION ---
DATASET_FILE = "dataset/skeletal_data.csv"
MODEL_DIR = "models"
MODEL_FILE = os.path.join(MODEL_DIR, "action_model.pkl")

print("\n" + "="*50)
print("    VANGUARD AI: NEURAL TRAINING ENGINE")
print("="*50)

if not os.path.exists(DATASET_FILE):
    print(f"[ERROR] Dataset not found at {DATASET_FILE}")
    print("Please run `python collect_data.py` to capture your custom data first!")
    exit()

print("[1/5] Loading Dataset...")
df = pd.read_csv(DATASET_FILE)

# Drop any rows with missing data (NaN) due to camera tracking glitches
df.dropna(inplace=True)

# Separate Features (X) and Labels (y)
X = df.drop('label', axis=1) # All the 132 kinematic columns (x,y,z,v)
y = df['label']              # 'Normal' or 'Aggressive'

print(f"[2/5] Dataset Loaded! Total Frames: {len(df)}")
print(f"      Labels found: {y.unique()}")

# Split data: 80% for Training, 20% for Testing/Validation
print("[3/5] Splitting data into Training & Testing suites...")
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# Initialize the Machine Learning Algorithm
# Random Forest is highly robust against overfitting and works perfectly on tabular coordinate data
print("[4/5] Training Custom Random Forest Classifier...")
model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
model.fit(X_train, y_train)

# Evaluate the model
print("[5/5] Evaluating Neural Weights...")
y_pred = model.predict(X_test)

accuracy = accuracy_score(y_test, y_pred)
print("\n" + "="*50)
print(f"   TRAINING COMPLETE: {accuracy * 100:.2f}% ACCURACY ACHIEVED!")
print("="*50)

print("\nDetailed Classification Report:")
print(classification_report(y_test, y_pred))

# Save the custom model file for main.py to consume
if not os.path.exists(MODEL_DIR):
    os.makedirs(MODEL_DIR)

with open(MODEL_FILE, 'wb') as f:
    pickle.dump(model, f)

print(f"\nSUCCESS \u2713 Model weights securely exported to: {MODEL_FILE}")
print("You can now run `main.py` to deploy your custom AI into the Dashboard!")
