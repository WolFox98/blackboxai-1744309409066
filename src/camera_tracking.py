import cv2 
import numpy as np
import mediapipe as mp
from pythonosc import udp_client
import threading
import logging
import tkinter as tk
from tkinter import ttk

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

def select_camera():
    """Mostra una finestra per selezionare la webcam"""
    root = tk.Tk()
    root.title("Seleziona Webcam")
    
    selected_camera = tk.IntVar(value=0)
    
    def test_camera(cam_id):
        cap = cv2.VideoCapture(cam_id)
        if cap.isOpened():
            ret, frame = cap.read()
            cap.release()
            return ret
        return False
    
    # Trova le webcam disponibili
    available_cameras = []
    for i in range(5):  # Testa le prime 5 webcam
        if test_camera(i):
            available_cameras.append(i)
    
    frame = ttk.Frame(root, padding="10")
    frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    
    ttk.Label(frame, text="Seleziona la webcam da usare:").grid(row=0, column=0, pady=5)
    
    for i, cam_id in enumerate(available_cameras):
        ttk.Radiobutton(
            frame, 
            text=f"Webcam {cam_id}", 
            variable=selected_camera, 
            value=cam_id
        ).grid(row=i+1, column=0, pady=2)
    
    def on_ok():
        root.quit()
        root.destroy()
    
    ttk.Button(frame, text="OK", command=on_ok).grid(row=len(available_cameras)+1, column=0, pady=10)
    
    root.mainloop()
    return selected_camera.get()

if __name__ == "__main__":
    camera_id = select_camera()
    tracker = CameraTracker()
    tracker.start_camera(camera_id)
    
    try:
        while True:
            pass
    except KeyboardInterrupt:
        tracker.stop_camera()
