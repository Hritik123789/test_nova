@echo off
echo ========================================
echo Restarting CityPulse Backend Server
echo ========================================
echo.

echo Stopping any existing backend processes...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq *api_v2.py*" 2>nul

echo.
echo Starting backend server on port 5000...
cd backend
start "CityPulse Backend" python api_v2.py

echo.
echo ========================================
echo Backend server started!
echo ========================================
echo.
echo Backend running at: http://localhost:5000
echo API endpoints: http://localhost:5000/
echo.
echo Press any key to exit...
pause >nul
