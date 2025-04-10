# SlimeVR Anti-Drift System

Questo sistema migliora il tracking di SlimeVR, risolvendo i problemi di drift e calibrazione, specialmente quando:
- Ti sdrai
- Alzi le gambe
- Fai movimenti che causano problemi di tracking

## Installazione Facile

### Per Windows:
1. Scarica questo pacchetto
2. Fai doppio click su `install.bat`
3. Se richiesto, indica dove hai installato SlimeVR

### Per Linux/macOS:
1. Scarica questo pacchetto
2. Apri il terminale nella cartella
3. Esegui:
   ```bash
   chmod +x install.sh
   ./install.sh
   ```
4. Se richiesto, indica dove hai installato SlimeVR

## Dopo l'Installazione

1. Riavvia SlimeVR
2. Apri nel browser: http://localhost:8080/web/advancedSettings.html
3. Usa l'interfaccia per:
   - Regolare la sensibilità del drift
   - Modificare la velocità di correzione
   - Eseguire la calibrazione

## Impostazioni Consigliate

- **Drift Threshold** (Sensibilità al drift)
  - Default: 5.0
  - Aumenta se il tracking è troppo sensibile
  - Diminuisci se il drift non viene corretto abbastanza velocemente

- **Filter Coefficient** (Smoothing)
  - Default: 0.85
  - Aumenta per movimenti più fluidi ma più lenti
  - Diminuisci per correzioni più rapide ma meno fluide

## Risoluzione Problemi

Se hai problemi dopo l'installazione:
1. Verifica che SlimeVR sia chiuso durante l'installazione
2. Controlla che il percorso di installazione sia corretto
3. Riavvia SlimeVR dopo l'installazione
4. Assicurati che la porta 8080 sia disponibile per l'interfaccia web

## Note

- Questo sistema si integra con l'app owoTracker esistente
- Non modifica i tuoi file originali di SlimeVR
- Puoi disinstallare in qualsiasi momento eliminando la cartella `anti-drift`

Per supporto o problemi, apri una issue su GitHub.
