import argparse
from pythonosc import dispatcher
from pythonosc import osc_server
from pythonosc import udp_client
import math
import threading
import time

class AntiDriftBridge:
    def __init__(self):
        # Configurazione client e server OSC
        self.client = udp_client.SimpleUDPClient("127.0.0.1", 9000)  # Porta di output SlimeVR
        self.drift_threshold = 5.0
        self.filter_coefficient = 0.85
        self.last_positions = {}
        self.reference_positions = {}
        self.is_calibrated = False

    def handle_tracker_data(self, address, *args):
        """Gestisce i dati in arrivo dai tracker"""
        tracker_id = address.split('/')[-1]
        
        if not self.is_calibrated:
            self.reference_positions[tracker_id] = list(args)
            return

        # Applica correzione drift
        corrected_data = self.apply_drift_correction(tracker_id, list(args))
        
        # Invia dati corretti a SlimeVR
        self.client.send_message(f"/tracker/{tracker_id}", corrected_data)

    def apply_drift_correction(self, tracker_id, current_data):
        """Applica la correzione del drift ai dati del tracker"""
        if tracker_id not in self.last_positions:
            self.last_positions[tracker_id] = current_data
            return current_data

        # Calcola il drift
        drift = [abs(c - l) for c, l in zip(current_data, self.last_positions[tracker_id])]
        
        # Se il drift supera la soglia, applica la correzione
        if max(drift) > self.drift_threshold:
            # Applica il filtro di Kalman semplificato
            corrected = []
            for i in range(len(current_data)):
                correction = (self.filter_coefficient * current_data[i] + 
                            (1 - self.filter_coefficient) * self.last_positions[tracker_id][i])
                corrected.append(correction)
            current_data = corrected

        self.last_positions[tracker_id] = current_data
        return current_data

    def calibrate(self):
        """Esegue la calibrazione"""
        print("Calibrazione in corso...")
        self.last_positions.clear()
        self.reference_positions.clear()
        self.is_calibrated = True
        print("Calibrazione completata!")

    def set_parameters(self, drift_threshold=None, filter_coefficient=None):
        """Imposta i parametri di correzione"""
        if drift_threshold is not None:
            self.drift_threshold = drift_threshold
        if filter_coefficient is not None:
            self.filter_coefficient = filter_coefficient

def main():
    bridge = AntiDriftBridge()
    
    # Configurazione server OSC
    dispatcher = dispatcher.Dispatcher()
    dispatcher.map("/tracker/*", bridge.handle_tracker_data)
    
    # Avvia il server sulla porta di input di SlimeVR
    server = osc_server.ThreadingOSCUDPServer(("127.0.0.1", 9002), dispatcher)
    
    print("Anti-Drift Bridge avviato!")
    print("In ascolto su porta 9002, invio su porta 9000")
    print("Premi Ctrl+C per uscire")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nChiusura Anti-Drift Bridge...")
        server.server_close()

if __name__ == "__main__":
    main()
