from flask import Flask, render_template, jsonify, request
import threading
from pythonosc import udp_client
import json
import os

app = Flask(__name__)
client = None
bridge_running = False

# Configurazione di base
config = {
    'drift_threshold': 5.0,
    'filter_coefficient': 0.85
}

@app.route('/')
def index():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>SlimeVR Anti-Drift Control</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            input[type="range"] {
                width: 100%;
            }
        </style>
    </head>
    <body class="bg-gray-100 p-8">
        <div class="max-w-2xl mx-auto bg-white p-6 rounded-lg shadow-lg">
            <h1 class="text-2xl font-bold mb-6">SlimeVR Anti-Drift Control</h1>
            
            <div class="mb-6">
                <label class="block text-sm font-medium text-gray-700 mb-2">
                    Drift Threshold: <span id="thresholdValue">5.0</span>
                </label>
                <input type="range" id="driftThreshold" min="1" max="10" step="0.1" value="5.0"
                       class="w-full h-2 bg-blue-200 rounded-lg appearance-none cursor-pointer">
                <p class="text-sm text-gray-500 mt-1">Higher values mean less sensitive drift detection</p>
            </div>

            <div class="mb-6">
                <label class="block text-sm font-medium text-gray-700 mb-2">
                    Filter Coefficient: <span id="coefficientValue">0.85</span>
                </label>
                <input type="range" id="filterCoefficient" min="0" max="1" step="0.01" value="0.85"
                       class="w-full h-2 bg-blue-200 rounded-lg appearance-none cursor-pointer">
                <p class="text-sm text-gray-500 mt-1">Higher values mean smoother but slower corrections</p>
            </div>

            <div class="flex space-x-4">
                <button onclick="calibrate()" 
                        class="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600 transition-colors">
                    Calibrate
                </button>
                <button onclick="saveSettings()" 
                        class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 transition-colors">
                    Save Settings
                </button>
            </div>

            <div id="status" class="mt-4 p-4 rounded hidden"></div>
        </div>

        <script>
            document.getElementById('driftThreshold').addEventListener('input', (e) => {
                document.getElementById('thresholdValue').textContent = e.target.value;
            });

            document.getElementById('filterCoefficient').addEventListener('input', (e) => {
                document.getElementById('coefficientValue').textContent = e.target.value;
            });

            function showStatus(message, isError = false) {
                const status = document.getElementById('status');
                status.textContent = message;
                status.className = `mt-4 p-4 rounded ${isError ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'}`;
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
                        showStatus('Settings saved successfully!');
                    } else {
                        showStatus('Failed to save settings', true);
                    }
                } catch (error) {
                    showStatus('Error saving settings: ' + error, true);
                }
            }

            async function calibrate() {
                try {
                    const response = await fetch('/calibrate', {method: 'POST'});
                    if (response.ok) {
                        showStatus('Calibration completed!');
                    } else {
                        showStatus('Calibration failed', true);
                    }
                } catch (error) {
                    showStatus('Error during calibration: ' + error, true);
                }
            }
        </script>
    </body>
    </html>
    """

@app.route('/settings', methods=['POST'])
def update_settings():
    global config
    data = request.json
    config.update(data)
    return jsonify({'status': 'success'})

@app.route('/calibrate', methods=['POST'])
def calibrate():
    # Implementa la calibrazione qui
    return jsonify({'status': 'success'})

def run_web_interface():
    app.run(host='127.0.0.1', port=9003)

if __name__ == '__main__':
    run_web_interface()
