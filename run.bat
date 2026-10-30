@echo off
title ClipMind AI
cd /d "%~dp0"

echo ========================================================
echo                 Starting ClipMind AI
echo ========================================================
echo.

:: Activate virtual environment
if exist ".venv\Scripts\activate.bat" (
    echo [OK] Activating environment: .venv
    call ".venv\Scripts\activate.bat"
    goto :START_APP
)

if exist "venv\Scripts\activate.bat" (
    echo [OK] Activating environment: venv
    call "venv\Scripts\activate.bat"
    goto :START_APP
)

echo [*] No virtual environment found. Using system Python.

:START_APP
echo.
echo [OK] Launching ClipMind AI...
echo [i] Open your browser at: http://localhost:8501
echo.

:: Use "python -m streamlit" instead of "streamlit" directly.
:: This avoids the broken wrapper .exe path resolution on some Windows setups.
python -m streamlit run app.py --server.headless false --browser.gatherUsageStats false

:: Keep window open if application exits with error
if errorlevel 1 (
    echo.
    echo ========================================================
    echo [ERROR] Application stopped unexpectedly.
    echo         Check the output above for details.
    echo ========================================================
    pause
)
