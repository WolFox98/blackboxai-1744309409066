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
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
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

                <div class="flex space-x-4">
                    <button onclick="startCamera()" id="cameraBtn"
                            class="bg-purple-500 text-white px-4 py-2 rounded hover:bg-purple-600 transition-colors flex-1">
                        <i class="fas fa-play mr-2"></i>Avvia Camera
                    </button>
                    <button onclick="stopCamera()" id="stopCameraBtn"
                            class="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600 transition-colors flex-1 hidden">
                        <i class="fas fa-stop mr-2"></i>Ferma Camera
                    </button>
                </div>
            </div>
        </div>
    </div>

    <div id="status" class="fixed bottom-4 right-4 hidden"></div>

    <script>
        // Slider updates
        document.getElementById('driftThreshold').addEventListener('input', (e) => {
            document.getElementById('thresholdValue').textContent = e.target.value;
        });

        document.getElementById('filterCoefficient').addEventListener('input', (e) => {
            document.getElementById('coefficientValue').textContent = e.target.value;
        });

        function showStatus(message, isError = false) {
            const status = document.getElementById('status');
            status.textContent = message;
            status.className = `fixed bottom-4 right-4 p-4 rounded ${isError ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'}`;
            status.style.display = 'block';
            setTimeout(() => status.style.display = 'none', 3000);
        }

        async function saveSettings() {
            const settings = {
                drift_threshold: parseFloat(document.getElementById('driftThreshold').value),
                filter_coefficient: parseFloat(document.getElementById('filterCoefficient').value)
            };

            try {
                const response = await fetch('/settings', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(settings)
                });

                if (response.ok) {
                    showStatus('Impostazioni salvate con successo!');
                } else {
                    showStatus('Errore nel salvare le impostazioni', true);
                }
            } catch (error) {
                showStatus('Errore: ' + error, true);
            }
        }

        async function calibrate() {
            try {
                const response = await fetch('/calibrate', {method: 'POST'});
                if (response.ok) {
                    showStatus('Calibrazione completata!');
                } else {
                    showStatus('Errore nella calibrazione', true);
                }
            } catch (error) {
                showStatus('Errore: ' + error, true);
            }
        }

        async function startCamera() {
            try {
                const response = await fetch('/start_camera', {method: 'POST'});
                if (response.ok) {
                    document.getElementById('cameraBtn').classList.add('hidden');
                    document.getElementById('stopCameraBtn').classList.remove('hidden');
                    showStatus('Camera avviata!');
                } else {
                    showStatus('Errore nell\'avvio della camera', true);
                }
            } catch (error) {
                showStatus('Errore: ' + error, true);
            }
        }

        async function stopCamera() {
            try {
                const response = await fetch('/stop_camera', {method: 'POST'});
                if (response.ok) {
                    document.getElementById('cameraBtn').classList.remove('hidden');
                    document.getElementById('stopCameraBtn').classList.add('hidden');
                    showStatus('Camera fermata!');
                } else {
                    showStatus('Errore nel fermare la camera', true);
                }
            } catch (error) {
                showStatus('Errore: ' + error, true);
            }
        }
    </script>
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

@app.route('/start_camera', methods=['POST'])
def start_camera():
    global camera_tracker
    try:
        if camera_tracker is None:
            camera_id = select_camera()
            camera_tracker = CameraTracker()
            if camera_tracker.start_camera(camera_id):
                return jsonify({'status': 'success'})
        return jsonify({'status': 'error', 'message': 'Camera già in esecuzione o errore di avvio'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

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
