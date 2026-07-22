@echo off
setlocal
echo ==============================================
echo    Starting AI Medical Imaging Application
echo    (Troubleshooting Version)
echo ==============================================

echo [1/4] Checking environment...
python --version >nul 2>&1
if %errorlevel% NEQ 0 (
    echo [ERROR] Python not found in PATH! Please install Python.
    pause
    exit /b
)

echo [2/4] Checking Port 5000 availability...
netstat -ano | findstr :5000 | findstr LISTENING >nul
if %errorlevel% EQU 0 (
    echo [WARNING] Port 5000 is already in use by another program.
    echo This might cause the backend to fail. 
    echo Please close other apps using port 5000 and try again.
    timeout /t 5
)

echo [3/4] Installing requirements...
cd backend
python -m pip install -r requirements.txt > nul 2>&1
cd ..

echo [4/4] Starting Flask Backend Server...
echo ----------------------------------------------
echo IMPORTANT: KEEP THE NEW WINDOW OPEN!
echo ----------------------------------------------
:: Opens a new command prompt window to show the server logs
start "Medical AI Backend" cmd /k "cd backend && python app.py"

echo Waiting for server to initialize (5 seconds)...
timeout /t 5 /nobreak > nul

echo Opening the Web Interface...
start "" "web_page\index.html"

echo Done!
echo If you see a 'Network Error' again, check the 'Medical AI Backend' window for errors.
timeout /t 10
exit
