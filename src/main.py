import threading
import sys
import os
import socket
from osc_bridge import AntiDriftBridge
from web_interface import run_web_interface
from pythonosc import osc_server
from pythonosc import dispatcher

def get_local_ip():
    """Ottiene l'indirizzo IPv4 locale del PC"""
    try:
        # Crea un socket UDP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Non serve una connessione reale
        s.connect(("8.8.8.8", 80))
        # Ottiene l'IP locale
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "Non trovato"

def main():
    local_ip = get_local_ip()
    
    print("SlimeVR Anti-Drift System")
    print("========================")
    print(f"\nIl tuo indirizzo IPv4: {local_ip}")
    print("\nUSA QUESTO INDIRIZZO IP IN OWOTRACKER!")
    print("----------------------------------------")
    print("\nConfigura owoTracker così:")
    print(f"- IP: {local_ip}")
    print("- Porta: 6969")
    print("\nAvvio del sistema...")

    # Crea e avvia il bridge OSC in un thread separato
    bridge = AntiDriftBridge()
    
    # Configurazione server OSC
    disp = dispatcher.Dispatcher()
    disp.map("/tracker/*", bridge.handle_tracker_data)
    
    # Avvia il server OSC in un thread separato
    server = osc_server.ThreadingOSCUDPServer(("0.0.0.0", 6969), disp)
    osc_thread = threading.Thread(target=server.serve_forever)
    osc_thread.daemon = True
    osc_thread.start()
    
    print("\n✓ Bridge OSC avviato")
    print("  - In ascolto sulla porta 6969")
    print("  - Invio a SlimeVR sulla porta 9002")

    # Avvia l'interfaccia web in un thread separato
    web_thread = threading.Thread(target=run_web_interface)
    web_thread.daemon = True
    web_thread.start()
    
    print("\n✓ Interfaccia web avviata")
    print("  - Disponibile su: http://localhost:9003")
    
    print("\nPassi da seguire:")
    print(f"1. In owoTracker, inserisci questo IP: {local_ip} e porta: 6969")
    print("2. Assicurati che SlimeVR sia in esecuzione")
    print("3. Apri l'interfaccia web nel tuo browser")
    print("4. Usa i controlli per regolare le impostazioni")
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
