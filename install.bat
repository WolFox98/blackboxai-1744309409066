@echo off
echo SlimeVR Anti-Drift System Installer
echo ================================
echo.

:: Verifica se Python è installato
python --version > nul 2>&1
if errorlevel 1 (
    echo Python non trovato! Per favore installa Python 3.x da python.org
    echo.
    pause
    exit /b 1
)

:: Installa le dipendenze necessarie
echo Installazione delle dipendenze...
pip install python-osc flask
if errorlevel 1 (
    echo Errore durante l'installazione delle dipendenze!
    pause
    exit /b 1
)
echo Dipendenze installate con successo!
echo.

:: Crea lo script di avvio
echo @echo off > run_anti_drift.bat
echo python src/main.py >> run_anti_drift.bat
echo pause >> run_anti_drift.bat

echo Installazione completata!
echo.
echo Per utilizzare il sistema:
echo 1. Assicurati che SlimeVR sia in esecuzione
echo 2. Esegui run_anti_drift.bat
echo 3. Configura owoTracker con l'IP che verrà mostrato
echo 4. Apri http://localhost:9003 nel browser
echo.
echo Avvio del programma...
echo.

:: Esegui il programma
python src/main.py
pause
