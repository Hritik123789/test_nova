@echo off
echo ========================================
echo CityPulse Data Refresh Scheduler
echo ========================================
echo.
echo This will run all agents every 3 hours
echo to keep your data fresh.
echo.
echo Press Ctrl+C to stop the scheduler
echo ========================================
echo.

cd agents
python scheduler.py

pause
