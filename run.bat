@echo off
echo Setting up Python virtual environment...
python -m venv venv

echo Creating global cache directory...
if not exist "global_cache" mkdir "global_cache"

echo Activating virtual environment...
call venv\Scripts\activate

echo Installing dependencies...
pip install -r Requirements.txt

REM Direct all __pycache__ to global_cache directory
set PYTHONPYCACHEPREFIX=global_cache

echo Starting Flask server...
python main.py

pause