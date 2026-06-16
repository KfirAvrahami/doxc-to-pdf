@echo off
REM Run this script on an INTERNET-CONNECTED machine that has the SAME Python
REM version and Windows architecture as the SAP application server.
REM
REM It downloads all required wheel files into the "wheels\" folder so you can
REM transfer them to the offline SAP server and install without internet access.
REM
REM Usage:
REM   download_wheels.bat
REM
REM After running, copy the entire "wheels\" folder to the SAP app server and
REM run install_offline.bat there.

echo Downloading wheel files for offline installation...
python -m pip download --dest wheels --only-binary=:all: -r requirements.txt

if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Download failed. Make sure you have internet access and pip installed.
    exit /b 1
)

echo.
echo Done. Copy the "wheels\" folder to the SAP application server.
echo Then run install_offline.bat on the target machine.
