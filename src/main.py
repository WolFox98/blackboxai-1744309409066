import threading
import sys
import os
from osc_bridge import AntiDriftBridge
from web_interface import run_web_interface
from pythonosc import osc_server
from pythonosc import dispatcher

def main():
    print("SlimeVR Anti-Drift System")
    print("========================")
    print("\nAvvio del sistema...")

    # Crea e avvia il bridge OSC in un thread separato
    bridge = AntiDriftBridge()
    
    # Configurazione server OSC
    disp = dispatcher.Dispatcher()
    disp.map("/tracker/*", bridge.handle_tracker_data)
    
    # Avvia il server OSC in un thread separato
    server = osc_server.ThreadingOSCUDPServer(("127.0.0.1", 9002), disp)
    osc_thread = threading.Thread(target=server.serve_forever)
    osc_thread.daemon = True
    osc_thread.start()
    
    print("\n✓ Bridge OSC avviato")
    print("  - In ascolto sulla porta 9002")
    print("  - Invio sulla porta 9000")

    # Avvia l'interfaccia web in un thread separato
    web_thread = threading.Thread(target=run_web_interface)
    web_thread.daemon = True
    web_thread.start()
    
    print("\n✓ Interfaccia web avviata")
    print("  - Disponibile su: http://localhost:9003")
    
    print("\nIstruzioni:")
    print("1. Assicurati che SlimeVR sia in esecuzione")
    print("2. Apri l'interfaccia web nel tuo browser")
    print("3. Usa i controlli per regolare le impostazioni")
    print("\nPremi Ctrl+C per uscire")

    try:
        # Mantieni il programma in esecuzione
        while True:
            input()
    except KeyboardInterrupt:
        print("\nChiusura del sistema...")
        server.shutdown()
        sys.exit(0)

if __name__ == "__main__":
    main()
