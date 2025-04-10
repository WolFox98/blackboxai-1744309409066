@echo off
echo SlimeVR Anti-Drift Installer
echo ===========================
echo.

:: Verifica se SlimeVR è installato
if exist "C:\Program Files\SlimeVR" (
    set SLIMEVR_PATH="C:\Program Files\SlimeVR"
) else if exist "C:\SlimeVR" (
    set SLIMEVR_PATH="C:\SlimeVR"
) else (
    echo Non riesco a trovare l'installazione di SlimeVR.
    echo Per favore, specifica il percorso di installazione di SlimeVR:
    set /p SLIMEVR_PATH=
)

echo.
echo Installazione in corso in %SLIMEVR_PATH%...
echo.

:: Crea le cartelle necessarie
mkdir "%SLIMEVR_PATH%\anti-drift"
mkdir "%SLIMEVR_PATH%\anti-drift\src"
mkdir "%SLIMEVR_PATH%\web"

:: Copia i file
copy "src\AntiDriftAlgorithm.h" "%SLIMEVR_PATH%\anti-drift\src\"
copy "src\AntiDriftAlgorithm.cpp" "%SLIMEVR_PATH%\anti-drift\src\"
copy "src\calibration.cpp" "%SLIMEVR_PATH%\anti-drift\src\"
copy "ui\advancedSettings.html" "%SLIMEVR_PATH%\web\"

:: Avvia un server Python per l'interfaccia web
echo.
echo Avvio del server web per l'interfaccia di configurazione...
start cmd /k "cd %SLIMEVR_PATH%\web && python -m http.server 9003"

echo.
echo Installazione completata!
echo.
echo Per utilizzare le nuove funzionalità:
echo 1. Assicurati che SlimeVR sia in esecuzione
echo 2. Apri nel browser: http://localhost:9003/advancedSettings.html
echo.
echo Premi un tasto per chiudere...
pause >nul
