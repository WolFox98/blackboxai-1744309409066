# SlimeVR Anti-Drift System

Questo sistema aiuta a correggere i problemi di drift in SlimeVR, specialmente quando:
- Ti sdrai
- Alzi le gambe
- Fai movimenti che causano problemi di tracking

## Come Funziona

Il sistema si posiziona tra owoTracker e SlimeVR:
1. Riceve i dati dai tracker sulla porta 9002
2. Applica correzioni in tempo reale
3. Invia i dati corretti a SlimeVR sulla porta 9000

```
owoTracker -> [Anti-Drift System] -> SlimeVR
```

## Requisiti

- Python 3.x (scaricabile da python.org)
- SlimeVR installato e funzionante
- owoTracker configurato

## Installazione

1. Scarica questo pacchetto
2. Esegui `install.bat` (Windows) o `install.sh` (Linux/macOS)
3. Segui le istruzioni sullo schermo

## Utilizzo

1. Avvia SlimeVR normalmente
2. Esegui `run_anti_drift.bat` (creato durante l'installazione)
3. Apri http://localhost:9003 nel browser
4. Usa l'interfaccia per:
   - Regolare la sensibilità del drift
   - Modificare la velocità di correzione
   - Eseguire la calibrazione

## Impostazioni

- **Drift Threshold** (Default: 5.0)
  - Controlla quanto il sistema è sensibile al drift
  - Valori più alti = meno sensibile
  - Valori più bassi = più sensibile

- **Filter Coefficient** (Default: 0.85)
  - Controlla quanto velocemente il sistema corregge il drift
  - Valori più alti = correzioni più fluide ma più lente
  - Valori più bassi = correzioni più rapide ma meno fluide

## Risoluzione Problemi

1. **L'interfaccia web non si apre**
   - Verifica che il programma sia in esecuzione
   - Controlla che la porta 9003 non sia in uso
   - Riavvia il programma

2. **Il tracking non migliora**
   - Prova a ricalibrare
   - Regola il Drift Threshold
   - Modifica il Filter Coefficient

3. **Errori di connessione**
   - Verifica che SlimeVR sia in esecuzione
   - Controlla che le porte 9000 e 9002 siano configurate correttamente in SlimeVR

## Note Tecniche

Il sistema utilizza:
- OSC (Open Sound Control) per la comunicazione
- Filtro di Kalman per la correzione del drift
- Flask per l'interfaccia web
- Python-OSC per la gestione dei dati dei tracker

## Supporto

Se hai problemi o domande:
1. Verifica la sezione "Risoluzione Problemi"
2. Controlla che tutte le porte (9000, 9002, 9003) siano disponibili
3. Assicurati di avere l'ultima versione di Python installata
