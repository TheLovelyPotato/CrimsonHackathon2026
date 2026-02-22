@echo off
REM Virtual Environment Setup Script for Windows

echo Creating virtual environment...
python -m venv venv

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing dependencies (if Requirements.txt exists)...
if exist Requirements.txt (
    pip install -r Requirements.txt
) else (
    echo No Requirements.txt found. Skipping dependency installation.
)

echo Virtual environment setup complete!
echo To activate in the future, run: venv\Scripts\activate.bat
echo To deactivate, run: deactivate
pause