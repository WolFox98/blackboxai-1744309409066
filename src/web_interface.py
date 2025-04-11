from flask import Flask, render_template_string, jsonify, request
import threading
from pythonosc import udp_client
import json
import os
from camera_tracking import CameraTracker, select_camera

app = Flask(__name__)
camera_tracker = None

# Template HTML integrato
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>SlimeVR Anti-Drift Control</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        // Funzione per aggiornare il valore visualizzato degli slider
        function updateValue(sliderId, valueId) {
            var value = document.getElementById(sliderId).value;
            document.getElementById(valueId).textContent = value;
        }

        // Funzione per mostrare messaggi di stato
        function showMessage(message, isError) {
            var status = document.getElementById('status');
            status.textContent = message;
            status.className = 'fixed bottom-4 right-4 p-4 rounded ' + 
                (isError ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700');
            status.style.display = 'block';
            setTimeout(function() { status.style.display = 'none'; }, 3000);
        }

        // Funzione per salvare le impostazioni
        function saveSettings() {
            var threshold = document.getElementById('driftThreshold').value;
            var coefficient = document.getElementById('filterCoefficient').value;
            
            fetch('/settings', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    drift_threshold: parseFloat(threshold),
                    filter_coefficient: parseFloat(coefficient)
                })
            })
            .then(function(response) {
                showMessage(response.ok ? 'Impostazioni salvate!' : 'Errore nel salvare', !response.ok);
            })
            .catch(function(error) {
                showMessage('Errore: ' + error, true);
            });
        }

        // Funzione per la calibrazione
        function calibrate() {
            fetch('/calibrate', { method: 'POST' })
            .then(function(response) {
                showMessage(response.ok ? 'Calibrazione completata!' : 'Errore nella calibrazione', !response.ok);
            })
            .catch(function(error) {
                showMessage('Errore: ' + error, true);
            });
        }

        // Gestione della camera
        var cameraActive = false;
        var previewInterval = null;

        function loadCameras() {
            fetch('/get_cameras')
            .then(response => response.json())
            .then(data => {
                const select = document.getElementById('cameraSelect');
                select.innerHTML = '<option value="">Seleziona una webcam...</option>';
                
                data.cameras.forEach(camera => {
                    const option = document.createElement('option');
                    option.value = camera.id;
                    option.textContent = camera.name;
                    select.appendChild(option);
                });

                if (data.cameras.length === 0) {
                    showMessage('Nessuna webcam trovata', true);
                }
            })
            .catch(error => {
                showMessage('Errore nel caricamento delle webcam: ' + error, true);
            });
        }

        function refreshCameras() {
            const refreshBtn = document.querySelector('button[onclick="refreshCameras()"] i');
            refreshBtn.className = 'fas fa-sync-alt fa-spin';
            loadCameras();
            setTimeout(() => {
                refreshBtn.className = 'fas fa-sync-alt';
            }, 1000);
        }

        function updatePreview() {
            if (cameraActive) {
                const preview = document.getElementById('cameraPreview');
                preview.src = '/get_frame?' + new Date().getTime();
            }
        }

        function toggleCamera() {
            const selectedCamera = document.getElementById('cameraSelect').value;
            if (!selectedCamera && !cameraActive) {
                showMessage('Seleziona una webcam prima di avviarla', true);
                return;
            }

            const endpoint = cameraActive ? '/stop_camera' : '/start_camera';
            const method = {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    camera_id: parseInt(selectedCamera)
                })
            };

            fetch(endpoint, method)
            .then(function(response) {
                if (response.ok) {
                    cameraActive = !cameraActive;
                    const btn = document.getElementById('cameraBtn');
                    const btnText = document.getElementById('cameraButtonText');
                    const btnIcon = btn.querySelector('i');
                    const previewContainer = document.getElementById('previewContainer');
                    
                    if (cameraActive) {
                        btn.className = 'bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600 transition-colors w-full';
                        btnIcon.className = 'fas fa-stop mr-2';
                        btnText.textContent = 'Ferma Camera';
                        previewContainer.className = 'block';
                        // Avvia l'aggiornamento della preview
                        previewInterval = setInterval(updatePreview, 100);
                    } else {
                        btn.className = 'bg-purple-500 text-white px-4 py-2 rounded hover:bg-purple-600 transition-colors w-full';
                        btnIcon.className = 'fas fa-play mr-2';
                        btnText.textContent = 'Avvia Camera';
                        previewContainer.className = 'hidden';
                        // Ferma l'aggiornamento della preview
                        if (previewInterval) {
                            clearInterval(previewInterval);
                            previewInterval = null;
                        }
                    }
                    showMessage(cameraActive ? 'Camera avviata!' : 'Camera fermata!', false);
                } else {
                    showMessage('Errore con la camera', true);
                }
            })
            .catch(function(error) {
                showMessage('Errore: ' + error, true);
            });
        }

        // Inizializzazione quando il documento è caricato
        document.addEventListener('DOMContentLoaded', function() {
            // Carica le webcam
            loadCameras();
            
            // Imposta i valori iniziali degli slider
            updateValue('driftThreshold', 'thresholdValue');
            updateValue('filterCoefficient', 'coefficientValue');

            // Aggiungi i listener per gli slider
            document.getElementById('driftThreshold').addEventListener('input', function() {
                updateValue('driftThreshold', 'thresholdValue');
            });
            document.getElementById('filterCoefficient').addEventListener('input', function() {
                updateValue('filterCoefficient', 'coefficientValue');
            });
        });
    </script>
</head>
<body class="bg-gray-100 p-8">
    <div class="max-w-4xl mx-auto space-y-8">
        <!-- Anti-Drift Controls -->
        <div class="bg-white p-6 rounded-lg shadow-lg">
            <div class="flex items-center space-x-3 mb-6">
                <i class="fas fa-cog text-blue-500 text-3xl"></i>
                <h1 class="text-2xl font-bold text-gray-800">Anti-Drift Controls</h1>
            </div>

            <div class="space-y-6">
                <div class="space-y-2">
                    <label class="block text-sm font-medium text-gray-700">
                        Drift Threshold: <span id="thresholdValue">5.0</span>
                    </label>
                    <input type="range" id="driftThreshold" min="1" max="10" step="0.1" value="5.0"
                           class="w-full h-2 bg-blue-200 rounded-lg appearance-none cursor-pointer">
                    <p class="text-sm text-gray-500">Valori più alti = rilevamento drift meno sensibile</p>
                </div>

                <div class="space-y-2">
                    <label class="block text-sm font-medium text-gray-700">
                        Filter Coefficient: <span id="coefficientValue">0.85</span>
                    </label>
                    <input type="range" id="filterCoefficient" min="0" max="1" step="0.01" value="0.85"
                           class="w-full h-2 bg-blue-200 rounded-lg appearance-none cursor-pointer">
                    <p class="text-sm text-gray-500">Valori più alti = correzioni più fluide ma più lente</p>
                </div>

                <div class="flex space-x-4">
                    <button onclick="calibrate()" 
                            class="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600 transition-colors flex-1">
                        <i class="fas fa-sync-alt mr-2"></i>Calibra
                    </button>
                    <button onclick="saveSettings()" 
                            class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 transition-colors flex-1">
                        <i class="fas fa-save mr-2"></i>Salva Impostazioni
                    </button>
                </div>
            </div>
        </div>

        <!-- Camera Tracking -->
        <div class="bg-white p-6 rounded-lg shadow-lg">
            <div class="flex items-center space-x-3 mb-6">
                <i class="fas fa-camera text-purple-500 text-3xl"></i>
                <h1 class="text-2xl font-bold text-gray-800">Camera Tracking</h1>
            </div>

            <div class="space-y-6">
                <div class="bg-purple-50 border-l-4 border-purple-500 p-4 rounded-r">
                    <p class="text-purple-700">
                        <i class="fas fa-info-circle mr-2"></i>
                        Usa la webcam per migliorare il tracking quando sei sdraiato o in posizioni difficili.
                    </p>
                </div>

                <div class="space-y-4">
                    <div class="flex items-center space-x-4">
                        <select id="cameraSelect" class="flex-1 p-2 border rounded">
                            <option value="">Seleziona una webcam...</option>
                        </select>
                        <button onclick="refreshCameras()" class="p-2 text-blue-500 hover:text-blue-600">
                            <i class="fas fa-sync-alt"></i>
                        </button>
                    </div>

                    <div id="previewContainer" class="hidden">
                        <img id="cameraPreview" class="w-full rounded-lg shadow-lg" alt="Camera Preview">
                    </div>

                    <button onclick="toggleCamera()" id="cameraBtn"
                            class="bg-purple-500 text-white px-4 py-2 rounded hover:bg-purple-600 transition-colors w-full">
                        <i class="fas fa-play mr-2"></i><span id="cameraButtonText">Avvia Camera</span>
                    </button>
                </div>
            </div>
        </div>
    </div>

    <div id="status" class="fixed bottom-4 right-4 hidden"></div>
</body>
</html>
"""

@app.route('/')
def index():
    return HTML_TEMPLATE

@app.route('/settings', methods=['POST'])
def update_settings():
    data = request.json
    # Qui implementeremo l'aggiornamento delle impostazioni
    return jsonify({'status': 'success'})

@app.route('/calibrate', methods=['POST'])
def calibrate():
    # Qui implementeremo la calibrazione
    return jsonify({'status': 'success'})

@app.route('/get_cameras', methods=['GET'])
def get_cameras():
    """Ottiene la lista delle webcam disponibili"""
    from camera_tracking import get_available_cameras
    cameras = get_available_cameras()
    return jsonify({'cameras': cameras})

@app.route('/start_camera', methods=['POST'])
def start_camera():
    global camera_tracker
    try:
        data = request.json
        camera_id = data.get('camera_id', 0)
        
        if camera_tracker is None:
            camera_tracker = CameraTracker()
            if camera_tracker.start_camera(camera_id):
                return jsonify({'status': 'success'})
        return jsonify({'status': 'error', 'message': 'Camera già in esecuzione o errore di avvio'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/get_frame', methods=['GET'])
def get_frame():
    """Ottiene un frame dalla webcam attiva"""
    global camera_tracker
    try:
        if camera_tracker and camera_tracker.camera:
            ret, frame = camera_tracker.camera.read()
            if ret:
                # Converti il frame in JPEG
                import cv2
                _, buffer = cv2.imencode('.jpg', frame)
                return buffer.tobytes(), 200, {'Content-Type': 'image/jpeg'}
    except Exception as e:
        pass
    return '', 404

@app.route('/stop_camera', methods=['POST'])
def stop_camera():
    global camera_tracker
    try:
        if camera_tracker is not None:
            camera_tracker.stop_camera()
            camera_tracker = None
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

def run_web_interface():
    app.run(host='127.0.0.1', port=9003)

if __name__ == '__main__':
    run_web_interface()
