# Women Safety AI System

An intelligent AI-powered surveillance system designed to enhance women's safety through real-time monitoring, gender detection, and automated alert systems.

## Features

- **Real-time Video Surveillance**: Live camera monitoring with motion detection
- **AI Gender Detection**: Advanced deep learning models for gender recognition
- **Threat Detection**: Motion-based anomaly detection with configurable sensitivity
- **Automated Email Alerts**: Instant notifications with video evidence
- **Web Dashboard**: Live monitoring interface with system logs
- **Evidence Management**: Automatic video recording and secure storage

## Requirements

- Python 3.7+
- OpenCV
- Flask
- Pillow (PIL)
- NumPy
- Pre-trained AI models (included)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/INVADERGOKU/shesecure-.git
cd shesecure-
```

2. Install dependencies:
```bash
pip install opencv-python flask pillow numpy
```

3. Run the application:
```bash
python main.py
```

4. Open your browser to `http://127.0.0.1:5000`

## Configuration

### Email Settings
Update the email configuration in `main.py`:
```python
SENDER_EMAIL = "your_email@gmail.com"
APP_PASSWORD = "your_app_password"
RECEIVER_EMAIL = "alert_recipient@gmail.com"
```

### Detection Parameters
Adjust sensitivity in `main.py`:
```python
NOISE_MOTION_PERCENT = 0.005      # Background noise threshold
AGGRESSIVE_MOTION_PERCENT = 0.06  # Threat detection threshold
EXPOSURE_SPIKE_PERCENT = 0.90     # Light change tolerance
COOLDOWN_TIME = 3                 # Seconds between alerts
```

## Usage

1. **Start the System**: Run `python main.py`
2. **Monitor Dashboard**: Access the web interface at `http://127.0.0.1:5000`
3. **View Live Feed**: Real-time camera feed with AI overlays
4. **Check Logs**: System activity and alert history
5. **Receive Alerts**: Automatic email notifications with evidence

## System Architecture

- **AI Engine**: OpenCV DNN with Caffe models for gender detection
- **Motion Detection**: Background subtraction using MOG2 algorithm
- **Web Interface**: Flask-based dashboard with live video streaming
- **Alert System**: SMTP email integration with video attachments
- **Evidence Storage**: Local file system with organized directory structure

## Security Features

- Secure email authentication
- Local evidence storage
- Configurable alert thresholds
- Real-time monitoring logs
- Threat level classification

## File Structure

```
├── main.py                 # Main application
├── AgeGender.py           # Age/gender detection script
├── templates/
│   └── index.html         # Web dashboard
├── evidence/              # Recorded video alerts
├── evidence_png/          # Extracted frame images
├── gender_net.caffemodel  # Gender detection model
├── gender_deploy.prototxt # Model configuration
└── haarcascade_frontalface_default.xml # Face detection
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is developed for educational and safety purposes.

## Disclaimer

This system is designed to enhance safety but should not replace professional security measures. Always ensure compliance with local laws and privacy regulations.