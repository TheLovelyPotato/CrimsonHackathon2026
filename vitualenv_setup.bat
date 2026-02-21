@echo off
REM Virtual Environment Setup Script for Windows

echo Creating virtual environment...
python -m venv venv

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing dependencies (if requirements.txt exists)...
if exist requirements.txt (
    pip install -r requirements.txt
) else (
    echo No requirements.txt found. Skipping dependency installation.
)

echo Virtual environment setup complete!
echo To activate in the future, run: venv\Scripts\activate.bat
echo To deactivate, run: deactivate
pause