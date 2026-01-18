from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
import cv2
import os
import time
import datetime
import base64
import numpy as np

from detector import detect_faces, extract_face_crop
from utils import decrypt_data, encrypt_data
from production_enrollment import ProductionEnrollment
from simple_recognition import get_simple_recognition

app = Flask(__name__, 
            static_folder='react-frontend/dist',
            static_url_path='')
app.secret_key = os.urandom(24)

# Enable CORS for development
CORS(app, resources={r"/*": {"origins": ["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:5173"]}})

# =========================
# Global state
# =========================
camera = None
recognition_active = False
enrollment_system = None
enrolling_user = None
last_recognized_user = {"name": None, "time": 0}
simple_recognition_instance = None
speech_initialized = False


def get_lazy_recognition():
    """Lazy load recognition system only when needed"""
    global simple_recognition_instance
    if simple_recognition_instance is None:
        print("🔄 Initializing face recognition system...")
        simple_recognition_instance = get_simple_recognition()
        print("✅ Face recognition ready")
    return simple_recognition_instance

def init_speech():
    """Initialize speech synthesizer only when needed"""
    global speech_initialized
    if not speech_initialized:
        print("🔄 Initializing speech synthesizer...")
        from speech_synthesizer import speak_name_once
        speech_initialized = True
        print("✅ Speech synthesizer ready")

# =========================
# Camera helpers
# =========================
def init_camera():
    global camera
    if camera is not None and camera.isOpened():
        return True

    # Try different indices and backends if default fails
    for index in [0, 1]:
        print(f"尝试初始化摄像头 {index}...")
        camera = cv2.VideoCapture(index, cv2.CAP_DSHOW)
        if camera.isOpened():
            # Test a frame
            ret, frame = camera.read()
            if ret and frame is not None:
                camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                print(f"✅ 摄像头 {index} 初始化成功")
                return True
            else:
                camera.release()
    
    # Try without CAP_DSHOW as a final fallback
    print("Trying to initialize camera 0 (without DSHOW)...")
    camera = cv2.VideoCapture(0)
    if camera.isOpened():
        print("✅ Camera 0 (without DSHOW) initialized successfully")
        return True
    
    print("❌All attempts to initialize the cameras failed")
    camera = None
    return False


def get_camera_frame():
    if camera is None or not camera.isOpened():
        return None
    ret, frame = camera.read()
    if not ret or frame is None:
        return None
    return frame


# =========================
# Routes
# =========================
@app.route('/')
def serve():
    if os.path.exists(app.static_folder) and os.path.exists(os.path.join(app.static_folder, 'index.html')):
        return send_from_directory(app.static_folder, 'index.html')
    return render_template('index.html')

@app.errorhandler(404)
def not_found(e):
    if os.path.exists(app.static_folder) and os.path.exists(os.path.join(app.static_folder, 'index.html')):
        return send_from_directory(app.static_folder, 'index.html')
    return "Not Found", 404

@app.route('/video_feed')
def video_feed():
    def generate_frames():
        global last_recognized_user
        while True:
            frame = get_camera_frame()
            
            if frame is None:
                # Create a black placeholder frame when camera is offline
                placeholder = np.zeros((480, 640, 3), dtype=np.uint8)
                cv2.putText(placeholder, "Camera Offline - Click 'Start Camera'", (100, 240), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                _, buffer = cv2.imencode('.jpg', placeholder)
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
                time.sleep(1.0) # Slow pulse when offline
                continue

            try:
                # Perform recognition and detection in one go if possible
                result_str = ""
                faces = []
                
                if recognition_active:
                    # Simple recognition already does detection internally
                    # To avoid double work, we can just use the detected faces from recognize_face if we modify it
                    # But for now, let's just do detection normally and recognition if needed
                    faces = detect_faces(frame)
                    if faces:
                        _, result_str = get_lazy_recognition().recognize_face(frame)
                        
                        # Update global status for frontend
                        if "(" in result_str and "%" in result_str:
                            name = result_str.split(" (")[0]
                            now = time.time()
                            if name != last_recognized_user["name"] or (now - last_recognized_user["time"] > 5):
                                last_recognized_user = {"name": name, "time": now}
                else:
                    faces = detect_faces(frame)

                # Draw on frame
                for (x1, y1, x2, y2) in faces:
                    color = (0, 255, 0) if result_str and "Unknown" not in result_str else (0, 0, 255)
                    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                    if result_str:
                        cv2.putText(frame, result_str, (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

                _, buffer = cv2.imencode('.jpg', frame)
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
            except Exception as e:
                print(f"Stream Error: {e}")
                time.sleep(0.1)
                
            time.sleep(0.01)

    return app.response_class(generate_frames(),
                               mimetype='multipart/x-mixed-replace; boundary=frame')


# =========================
# Camera control
# =========================
@app.route('/api/start_camera', methods=['POST'])
@app.route('/start_camera', methods=['POST'])
def start_camera():
    global recognition_active
    if init_camera():
        recognition_active = True
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'Camera failed to start'}), 500


@app.route('/api/stop_camera', methods=['POST'])
@app.route('/stop_camera', methods=['POST'])
def stop_camera():
    global camera, recognition_active
    try:
        if camera:
            camera.release()
            camera = None
        recognition_active = False
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/status')
def status():
    # Return minimal status with latest recognition
    try:
        recognition = get_lazy_recognition()
        enrolled_users = len(recognition.known_names)
        users = recognition.known_names
    except:
        enrolled_users = 0
        users = []
    
    return jsonify({
        'camera_active': camera is not None and camera.isOpened(),
        'recognition_active': recognition_active,
        'enrolled_users': enrolled_users,
        'users': users,
        'latest_recognition': last_recognized_user
    })


# =========================
# Simple Recognition
# =========================
@app.route('/api/recognize', methods=['POST'])
@app.route('/recognize', methods=['POST'])
@app.route('/api/simple/recognize', methods=['POST'])
def simple_recognize():
    if camera is None or not camera.isOpened():
        return jsonify({'error': 'Camera not available'}), 400

    frame = get_camera_frame()
    if frame is None:
        return jsonify({'error': 'Cannot capture frame'}), 400

    face_crop, result = get_lazy_recognition().recognize_face(frame)

    if face_crop is None:
        return jsonify({'success': False, 'result': result})

    # Recognition results
    name = "Unknown"
    confidence = 0.0
    is_recognized = False
    
    if "(" in result and "%" in result:
        name = result.split(" (")[0]
        confidence_str = result.split("(")[1].split("%")[0]
        try:
            confidence = float(confidence_str)
            is_recognized = True
        except:
            pass

    _, buffer = cv2.imencode('.jpg', face_crop)
    face_b64 = base64.b64encode(buffer).decode()

    return jsonify({
        'success': True,
        'name': name,
        'identity': name,
        'result': result,
        'confidence': f"{confidence:.1f}%" if is_recognized else "0.0%",
        'face_image': f"data:image/jpeg;base64,{face_b64}",
        'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })


# =========================
# Multi-Pose Enrollment
# =========================
@app.route('/api/enrollment/start', methods=['POST'])
def start_enrollment():
    global enrollment_system, enrolling_user
    data = request.get_json()
    name = data.get('name')
    
    if not name:
        return jsonify({'success': False, 'error': 'Name is required'}), 400
        
    enrollment_system = ProductionEnrollment()
    enrolling_user = name
    enrollment_system.captured_images = {}
    
    return jsonify({
        'success': True,
        'message': f"Starting enrollment for {name}",
        'current_pose': enrollment_system.get_pose_instructions(),
        'pose_index': 0,
        'total_poses': len(enrollment_system.enrollment_poses)
    })

@app.route('/api/enrollment/capture', methods=['POST'])
def capture_pose():
    global enrollment_system, enrolling_user
    if not enrollment_system or not enrolling_user:
        return jsonify({'success': False, 'error': 'Enrollment not started'}), 400
        
    frame = get_camera_frame()
    if frame is None:
        return jsonify({'success': False, 'error': 'No camera frame'}), 400
        
    faces = detect_faces(frame)
    if not faces:
        return jsonify({'success': False, 'error': 'No face detected in frame'}), 400
        
    # Get current pose
    pose = enrollment_system.enrollment_poses[enrollment_system.current_pose_index]
    
    # Extract face and store
    bbox = faces[0]
    face_img = extract_face_crop(frame, bbox)
    
    if face_img is None:
        return jsonify({'success': False, 'error': 'Could not extract face'}), 400
        
    if pose not in enrollment_system.captured_images:
        enrollment_system.captured_images[pose] = []
    
    enrollment_system.captured_images[pose].append(face_img)
    
    # Move to next pose or complete
    enrollment_system.current_pose_index += 1
    
    if enrollment_system.current_pose_index >= len(enrollment_system.enrollment_poses):
        # Save and complete
        enrollment_system.save_face_images(enrolling_user, enrollment_system.captured_images)
        enrollment_system.update_encrypted_data(enrolling_user)
        
        # Reset simple recognition to load new user
        get_lazy_recognition().load_known_faces()
        
        user_name = enrolling_user
        enrolling_user = None
        enrollment_system = None
        
        return jsonify({
            'success': True,
            'complete': True,
            'message': f"Enrollment successful for {user_name}!"
        })
    else:
        next_pose = enrollment_system.enrollment_poses[enrollment_system.current_pose_index]
        return jsonify({
            'success': True,
            'complete': False,
            'next_pose': enrollment_system.get_pose_instructions(),
            'pose_index': enrollment_system.current_pose_index,
            'message': f"Captured {pose}! Next: {next_pose}"
        })

@app.route('/api/enrollment/cancel', methods=['POST'])
def cancel_enrollment():
    global enrollment_system, enrolling_user
    enrollment_system = None
    enrolling_user = None
    return jsonify({'success': True, 'message': 'Enrollment cancelled'})


# =========================
# Simple Enrollment
# =========================
@app.route('/api/simple/enroll', methods=['POST'])
def simple_enroll():
    data = request.get_json()
    user_name = data.get('name')

    if not user_name:
        return jsonify({'error': 'User name required'}), 400

    if camera is None or not camera.isOpened():
        return jsonify({'error': 'Camera not available'}), 400

    frame = get_camera_frame()
    if frame is None:
        return jsonify({'error': 'Cannot capture frame'}), 400

    success, message = get_lazy_recognition().add_new_user(frame, user_name)

    if success:
        return jsonify({'success': True, 'message': message})
    else:
        return jsonify({'success': False, 'error': message}), 400


@app.route('/api/simple/status')
def simple_status():
    return jsonify({
        'success': True,
        'camera_active': camera is not None and camera.isOpened(),
        'users': get_lazy_recognition().known_names
    })

# =========================
# Attendance & Users
# =========================
@app.route('/api/attendance')
def get_attendance():
    # Return empty list as attendance is removed
    return jsonify([])

@app.route('/api/users')
def get_users():
    users = get_lazy_recognition().known_names
    return jsonify(users)

@app.route('/api/users/<name>', methods=['DELETE'])
def delete_user(name):
    success, message = get_lazy_recognition().delete_user(name)
    if success:
        return jsonify({'success': True, 'message': message})
    return jsonify({'success': False, 'error': message}), 404


# =========================
# App start
# =========================
if __name__ == '__main__':
    print("🌐 Server starting at http://localhost:5000")
    print("💡 Camera and recognition will initialize on demand")
    app.run(host='0.0.0.0', port=5000, debug=False)

