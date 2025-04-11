import cv2 
import numpy as np
import mediapipe as mp
from pythonosc import udp_client
import threading
import logging

class CameraTracker:
    def __init__(self):
        self.running = False
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            model_complexity=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.8
        )
        self.client = udp_client.SimpleUDPClient("127.0.0.1", 9002)
        self.camera = None
        self.tracking_thread = None

    def start_camera(self, camera_id=0):
        """Avvia il tracking della webcam"""
        if self.camera is not None:
            self.stop_camera()
            
        self.camera = cv2.VideoCapture(camera_id)
        if not self.camera.isOpened():
            logging.error(f"Impossibile aprire la webcam {camera_id}")
            return False
            
        self.running = True
        self.tracking_thread = threading.Thread(target=self._tracking_loop)
        self.tracking_thread.daemon = True
        self.tracking_thread.start()
        return True

    def stop_camera(self):
        """Ferma il tracking della webcam"""
        self.running = False
        if self.tracking_thread:
            self.tracking_thread.join()
        if self.camera:
            self.camera.release()
        self.camera = None

    def _tracking_loop(self):
        """Loop principale per il tracking"""
        while self.running:
            ret, frame = self.camera.read()
            if not ret:
                continue

            # Converti l'immagine in RGB per MediaPipe
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.pose.process(rgb_frame)

            if results.pose_landmarks:
                # Estrai i dati rilevanti
                landmarks = results.pose_landmarks.landmark
                
                # Calcola posizione dell'anca
                hip_position = self._calculate_hip_position(landmarks)
                
                # Calcola posizione del torace
                chest_position = self._calculate_chest_position(landmarks)
                
                # Calcola posizione dei piedi
                left_foot = self._calculate_foot_position(landmarks, 'left')
                right_foot = self._calculate_foot_position(landmarks, 'right')

                # Invia i dati tramite OSC
                self._send_tracking_data({
                    'hip': hip_position,
                    'chest': chest_position,
                    'left_foot': left_foot,
                    'right_foot': right_foot
                })

    def _calculate_hip_position(self, landmarks):
        """Calcola la posizione dell'anca"""
        left_hip = landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value]
        right_hip = landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP.value]
        
        return {
            'position': [
                (left_hip.x + right_hip.x) / 2,
                (left_hip.y + right_hip.y) / 2,
                (left_hip.z + right_hip.z) / 2
            ],
            'rotation': [0, 0, 0],  # Rotazione base
            'visible': left_hip.visibility > 0.5 and right_hip.visibility > 0.5
        }

    def _calculate_chest_position(self, landmarks):
        """Calcola la posizione del torace"""
        left_shoulder = landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value]
        right_shoulder = landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
        
        return {
            'position': [
                (left_shoulder.x + right_shoulder.x) / 2,
                (left_shoulder.y + right_shoulder.y) / 2,
                (left_shoulder.z + right_shoulder.z) / 2
            ],
            'rotation': [0, 0, 0],  # Rotazione base
            'visible': left_shoulder.visibility > 0.5 and right_shoulder.visibility > 0.5
        }

    def _calculate_foot_position(self, landmarks, side):
        """Calcola la posizione del piede (sinistro o destro)"""
        if side == 'left':
            ankle = landmarks[self.mp_pose.PoseLandmark.LEFT_ANKLE.value]
            heel = landmarks[self.mp_pose.PoseLandmark.LEFT_HEEL.value]
        else:
            ankle = landmarks[self.mp_pose.PoseLandmark.RIGHT_ANKLE.value]
            heel = landmarks[self.mp_pose.PoseLandmark.RIGHT_HEEL.value]
        
        return {
            'position': [
                (ankle.x + heel.x) / 2,
                (ankle.y + heel.y) / 2,
                (ankle.z + heel.z) / 2
            ],
            'rotation': [0, 0, 0],  # Rotazione base
            'visible': ankle.visibility > 0.5 and heel.visibility > 0.5
        }

    def _send_tracking_data(self, data):
        """Invia i dati di tracking tramite OSC"""
        for tracker_id, tracker_data in data.items():
            if tracker_data['visible']:
                # Invia posizione
                self.client.send_message(
                    f"/tracker/{tracker_id}/position",
                    tracker_data['position']
                )
                # Invia rotazione
                self.client.send_message(
                    f"/tracker/{tracker_id}/rotation",
                    tracker_data['rotation']
                )

def get_available_cameras():
    """Trova tutte le webcam disponibili"""
    available_cameras = []
    
    def test_camera(cam_id):
        cap = cv2.VideoCapture(cam_id)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                # Ottieni il nome della webcam se possibile
                name = f"Camera {cam_id}"
                try:
                    name = cap.getBackendName() + f" ({cam_id})"
                except:
                    pass
                available_cameras.append({"id": cam_id, "name": name})
            cap.release()
        return False
    
    # Testa le prime 5 webcam
    for i in range(5):
        test_camera(i)
    
    return available_cameras

def select_camera():
    """Trova la prima webcam disponibile"""
    cameras = get_available_cameras()
    return cameras[0]["id"] if cameras else 0

if __name__ == "__main__":
    camera_id = select_camera()
    tracker = CameraTracker()
    tracker.start_camera(camera_id)
    
    try:
        while True:
            pass
    except KeyboardInterrupt:
        tracker.stop_camera()
