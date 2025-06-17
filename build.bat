@echo off

REM Build AzanScheduler executable
pyinstaller AzanSchedular.spec
echo Build complete. Check the dist folder for AzanScheduler.exe
pause