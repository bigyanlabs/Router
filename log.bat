@echo off
echo Starting Log Server...

REM Activate virtual environment
call venv\Scripts\activate

REM Start the log server on port 9001
python log.py 9001

pause