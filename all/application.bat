@echo off
echo ==============================================
echo    Starting Flutter Application (Frontend)
echo ==============================================

cd frontend
echo Executing Flutter on Chrome browser to avoid Windows Build issues...
flutter run -d chrome

pause
