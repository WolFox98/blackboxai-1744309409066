#!/bin/bash

echo "SlimeVR Anti-Drift Installer"
echo "==========================="
echo

# Possibili percorsi di installazione
POSSIBLE_PATHS=(
    "/opt/slimevr"
    "~/SlimeVR"
    "/Applications/SlimeVR"
)

# Trova l'installazione di SlimeVR
SLIMEVR_PATH=""
for path in "${POSSIBLE_PATHS[@]}"; do
    if [ -d "$path" ]; then
        SLIMEVR_PATH="$path"
        break
    fi
done

# Se non trovato, chiedi all'utente
if [ -z "$SLIMEVR_PATH" ]; then
    echo "Non riesco a trovare l'installazione di SlimeVR."
    echo "Per favore, specifica il percorso di installazione di SlimeVR:"
    read -r SLIMEVR_PATH
fi

echo
echo "Installazione in corso in $SLIMEVR_PATH..."
echo

# Crea le cartelle necessarie
mkdir -p "$SLIMEVR_PATH/anti-drift/src"
mkdir -p "$SLIMEVR_PATH/web"

# Copia i file
cp src/AntiDriftAlgorithm.h "$SLIMEVR_PATH/anti-drift/src/"
cp src/AntiDriftAlgorithm.cpp "$SLIMEVR_PATH/anti-drift/src/"
cp src/calibration.cpp "$SLIMEVR_PATH/anti-drift/src/"
cp ui/advancedSettings.html "$SLIMEVR_PATH/web/"

# Imposta i permessi
chmod 644 "$SLIMEVR_PATH/anti-drift/src/"*
chmod 644 "$SLIMEVR_PATH/web/advancedSettings.html"

# Avvia un server Python per l'interfaccia web
echo
echo "Avvio del server web per l'interfaccia di configurazione..."
python3 -m http.server 9003 --directory "$SLIMEVR_PATH/web" &

echo
echo "Installazione completata!"
echo
echo "Per utilizzare le nuove funzionalità:"
echo "1. Assicurati che SlimeVR sia in esecuzione"
echo "2. Apri nel browser: http://localhost:9003/advancedSettings.html"
echo
echo "Premi Invio per chiudere..."
read -r
