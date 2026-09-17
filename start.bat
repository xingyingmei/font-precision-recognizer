@echo off
REM Font Precision Recognizer - Windows Startup Script

setlocal

echo 🎨 Font Precision Recognizer - Startup Script
echo ==============================================

where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python is not installed or not in PATH.
    echo Please install Python 3.8+ and try again.
    pause
    exit /b 1
)

echo Checking if virtual environment exists...
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
    echo Virtual environment created.
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing dependencies...
pip install -r requirements.txt

echo Creating data directories...
if not exist data mkdir data
if not exist logs mkdir logs
if not exist static\images mkdir static\images

echo Initializing database...
python - <<'PY'
import os, json

data_dir = './data'
os.makedirs(data_dir, exist_ok=True)
db_path = os.path.join(data_dir, 'font_database.json')
if not os.path.exists(db_path):
    initial_db = {
        'version': '1.0.0',
        'last_updated': '2026-09-16',
        'fonts': []
    }
    with open(db_path, 'w', encoding='utf-8') as f:
        json.dump(initial_db, f, indent=2)
    print('Font database initialized')
else:
    print('Font database already exists')
PY

echo.
echo ==============================================
echo Startup complete.
echo Server will run on: http://localhost:5000

echo.
echo Press Ctrl+C to stop the server.
echo.

python app.py
