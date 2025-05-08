@echo off
REM Activate the virtual environment
call venv\Scripts\activate.bat

REM Start main.py in a new terminal
start cmd /k "python src\main.py"

REM Wait for a moment to ensure main.py is running
timeout /t 2

REM Start gui.py in a new terminal
start cmd /k "python src\gui.py"

REM Deactivate the virtual environment in the original terminal
call venv\Scripts\deactivate.bat
