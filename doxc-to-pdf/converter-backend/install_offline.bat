@echo off
REM Run this script on the SAP APPLICATION SERVER (offline environment).
REM The "wheels\" folder must be present in the same directory as this script.
REM
REM Usage:
REM   install_offline.bat
REM
REM This installs dxpdf and all its dependencies from local wheel files only,
REM without requiring any internet connection.

if not exist wheels\ (
    echo ERROR: "wheels\" folder not found.
    echo Copy the wheels\ folder from the internet-connected machine first.
    exit /b 1
)

echo Installing packages from local wheels (no internet required)...
python -m pip install --no-index --find-links=wheels\ -r requirements.txt

if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Installation failed.
    echo Make sure the wheel files match your Python version and Windows architecture.
    exit /b 1
)

echo.
echo Installation complete. Test the converter:
echo   python convert.py "C:\path\to\input.docx" "C:\path\to\output.pdf"
